#!/usr/bin/env python3

import argparse
import math
import os
import platform
import sys
import zlib
from argparse import Namespace

import humanize
import mmh3

PROG_NAME = "findup"
PROG_VERSION = "1.0"
COPYRIGHT = "Copyright (c) Kirill Shirokov, 2022-2025"


# Globals
""" Min. memory buffer size for reading files when calculating hashes and doing binary comparisons """
INTERNAL_FILE_BUFFER_SIZE: int = 8 * 1024 * 1024

""" Parsed program arguments """
ARGS: Namespace = Namespace()

""" All found files grouped by size """
FILES_BY_SIZE: dict[int, set[str]] = {}
""" Size per each found file """
SIZE_BY_FILE: dict[str, int] = {}
""" Filesystem cluster size in bytes per path given in arguments. Used to calculate wasted disk space """
CLUSTER_SIZE_BY_PATH: dict[str, int] = {}


def main() -> None:
    """
    Main functionality:
    1. parses arguments,
    2. obtains paths to scan,
    3. adds all files in these paths into global tables above,
    4. finds and reports duplicates
    """
    global ARGS
    ARGS = process_args()

    paths = get_paths()

    for path in paths:
        save_cluster_size(path)
        add_files(path)

    find_duplicates()


def get_paths() -> list[str]:
    """
    Extracts list of directory paths to scan from argument file or stdin (-i option) plus command-line arguments.

    :return: List of directory paths to scan, or emtpy list if none
    """
    dirlist = []
    if ARGS.paths_file:
        dirlist.extend([line.strip() for line in ARGS.paths_file])

    if ARGS.paths:
        dirlist.extend(ARGS.paths)

    return dirlist


def add_files(path: str) -> None:
    """
    Scans the path for the subdirectories and files. Invokes itself recursively for subdirectories.
    Adds files to the global list of candidate files. If the path does not exist, just does nothing.

    :param path: Filesystem path to scan.
    """
    print_verbose1(f"Scanning {path}:")

    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            add_files(os.path.join(root, dir_name))
        for file_name in files:
            add_file(os.path.join(root, file_name))


def save_cluster_size(path: str) -> None:
    """
    Saves cluster size for given path into a global variable CLUSTER_SIZE_BY_PATH.
    Cluster size is used to calculate wasted disk space due to duplicates. Exceptions are silently ignored.

    :param path: Path to find cluster size for
    """
    try:
        cluster_size = fs_cluster_size(path)
        CLUSTER_SIZE_BY_PATH[path] = cluster_size
        print_verbose2(f"Cluster size: {humanize.naturalsize(cluster_size)}")

    except OSError as ex:
        print_verbose3(f"Error obtaining cluster size for {path}: {ex}")


def add_file(file_name: str) -> None:
    """
    Adds a file to global list of candidates (FILES_BY_SIZE, SIZE_BY_FILE).
    File is not added if its size is less than the minimal (see program arguments).

    :param file_name: File name to add
    """
    file_size = os.path.getsize(file_name)

    if file_size < ARGS.min_file_size:
        print_verbose2(f"    SKIPPED: {file_name}: {file_size} bytes (too small)")
        return

    print_verbose2(f"    {file_name}: {file_size} bytes")

    FILES_BY_SIZE.setdefault(file_size, set()).add(file_name)
    SIZE_BY_FILE[file_name] = file_size


def find_duplicates() -> None:
    """
    Searches for duplicates and prints them and/or executes a scripts. Calculates and reports wasted space.
    Files are grouped first by size (in add_file() function), within groups, hashes are calculated for file prefix
    (see --prefix argument), creating more groups if necessary. After that in each group, hashes are calculated
    for the full file contents, creating even more groups, if needed.
    So far all comparisons have been of O(n) complexity. However, if user specified --paranoid program argument,
    within the groups from the last step, we compare the contents of the files byte-by-byte to create even more groups
    if needed (O(n^2) complexity). Normally --paranoid should not be needed, as having a collision in two hashes
    (crc32 and mmh3) are rare. If user is still not satisfied, it is perhaps a time to seek a spiritual teacher :)

    Total number of duplicate files (minus original ones!) and wasted space (again, minus the original one)
    is calculated. "Original" file is selected as the first in the alphabetical list of full paths.
    """
    print_verbose1("Finding duplicates...")
    total_wasted_disk_space = 0
    total_duplicates = 0

    for size, file_names in FILES_BY_SIZE.items():
        if len(file_names) < 2:
            continue

        file_by_prefix_hash = group_by_prefix_hash(file_names, size)
        file_by_hash = group_by_entire_file_hash(file_by_prefix_hash)
        file_groups = group_by_hash_or_contents(file_by_hash)

        for group_hash, groups_by_hash in file_groups.items():
            for group in groups_by_hash:
                if len(group) < 2:
                    continue

                duplicate_count = len(group) - 1
                wasted_disk_space = 0
                for cur_file_name in group[1:]:
                    wasted_disk_space += round_file_size(cur_file_name, size)

                print_normal(f"Duplicates (wasted {humanize.naturalsize(wasted_disk_space)}):\n    {'\n    '.join(group)}")

                execute_command_on_identical_files(group_hash, group)

                total_wasted_disk_space += wasted_disk_space
                total_duplicates += duplicate_count

    print_summary(f"Total wasted disk space in {str(total_duplicates)} files: "
                  f"{humanize.naturalsize(total_wasted_disk_space)}")


def group_by_prefix_hash(file_names: set[str], size: int) -> dict[str, set[str]]:
    """
    For each given file name calculates hash (crc32 + mmh3) of the first <size> bytes of the file and
    groups the file names by the hash. Returns a dict: hash -> [list of files with the same hash].

    :param file_names: File names to calculate the hash for
    :param size: The size of the files (since we first group files by size, all file_names will be of the same size)
    :return: dict containing sets of files grouped by hash
    """
    file_by_prefix_hash = {}
    prefix_size = min(size, ARGS.prefix_size)

    for file_name in file_names:
        file_prefix_hash = calc_file_hash(file_name, prefix_size)
        file_by_prefix_hash.setdefault(file_prefix_hash, set()).add(file_name)

    return file_by_prefix_hash


def group_by_entire_file_hash(file_by_prefix_hash: dict[str, set[str]]) -> dict[str, set[str]]:
    """
    For each dict value given in the argument calculates hash (crc32 + mmh3) of the entire file and
    groups the file names by the hash. Skips an entry if there are just one or no files in it.
    Returns a dict: hash -> [list of files with the same hash].

    :param file_by_prefix_hash: An output from group_by_prefix_hash():
           a dict: hash -> [names of the files with the same hash]
    :return: a dict: hash -> [names of the files with the same hash (of entire file)]
    """
    file_by_hash = {}

    for group_hash, same_hash_file_names in file_by_prefix_hash.items():
        if len(same_hash_file_names) < 2:
            continue

        print_verbose2(f"Processing identical hash group:\n    {'\n    '.join(same_hash_file_names)}\n")

        for file_name in same_hash_file_names:
            file_hash = calc_file_hash(file_name)
            file_by_hash.setdefault(file_hash, set()).add(file_name)

    return file_by_hash


def calc_file_hash(file_name: str, size: int = None) -> str:
    """
    Calculates hash of first size bytes of the file_name or entire file if size is None.

    Reads file contents into a limited buffer in order to keep memory consumption moderate.

    :param file_name File to calculate the hash for
    :param size How many bytes to include into hash from the beginning, or None to calculate for the entire file
    """
    print_verbose3("Calculating hash for "
                   f"{'first ' + str(size) + ' bytes of ' if size else ''}{file_name}: ",
                   end='')

    if ARGS.mock_prefix_hash and not size:
        print_verbose3(f"{ARGS.mock_prefix_hash}")
        return ARGS.mock_prefix_hash

    if ARGS.mock_full_hash and size:
        print_verbose3(f"{ARGS.mock_full_hash}")
        return ARGS.mock_full_hash

    if not size:
        size = SIZE_BY_FILE[file_name]

    buffer_size = max(INTERNAL_FILE_BUFFER_SIZE, get_cluster_size(file_name))
    offset = 0
    hash1 = 0
    hash2 = 0
    with open(file_name, 'rb') as f:
        while offset < size:
            buffer = f.read(min(buffer_size, size - offset))
            if not buffer:
                break
            hash1 = zlib.crc32(buffer, hash1)
            hash2 = mmh3.hash(buffer, hash2)
            offset += len(buffer)

    file_hash = str(hash1) + "_" + str(hash2)
    print_verbose3(f"{file_hash}")
    return file_hash


def group_by_hash_or_contents(file_by_hash: dict[str, set[str]]) -> dict[str, list[list[str]]]:
    """
    If user has specified --paranoid argument, this method will perform binary file comparisons inside groups,
    adding more groups when needed. If no such argument provided, output is basically the input with
    groups sorted alphabetically

    :param file_by_hash: Files already grouped by hash
    :return: Files grouped by exact contents, sorted alphabetically within group
    """
    file_groups = {}

    for group_hash, cur_file_names in file_by_hash.items():
        if len(cur_file_names) < 2:
            continue

        sorted_file_names = sorted(list(cur_file_names))

        if ARGS.paranoid:
            file_groups.setdefault(group_hash, list()).extend(paranoid_compare_files(sorted_file_names))
        else:
            file_groups.setdefault(group_hash, list()).append(sorted_file_names)

    return file_groups


def paranoid_compare_files(sorted_file_names: list[str]) -> list[list[str]]:
    """
    Compares files byte-by-byte and groups them into file having exactly the same contents.
    Takes each file in order and tries to find a group for it by comparing with the first file in the group.
    Worst case complexity is O(n^2).

    Called for files having the same hash when --paranoid argument is given.

    :param sorted_file_names: list of names of the files to compare
    :return: list of groups. Each group is the list of files having exactly the same content
    """
    file_groups = []

    for cur_file_name in sorted_file_names:
        found_group = False

        for group in file_groups:
            if are_files_binary_identical(cur_file_name, group[0]):
                group.append(cur_file_name)
                found_group = True
                break

        if not found_group:
            file_groups.append([cur_file_name])

    return file_groups


def are_files_binary_identical(file1: str, file2: str) -> bool:
    """
    Does binary comparison of the files, reading them in buffers of max(cluster size, 1MB).

    Reads file contents into a limited buffer in order to keep memory consumption moderate.

    :param file1: A file to compare
    :param file2: The other file to compare
    :return: true if the files are binary equal
    """
    print_verbose1("Binary comparing " + file1 + " vs " + file2 + ": ", end='')

    buffer_size = max(INTERNAL_FILE_BUFFER_SIZE, get_cluster_size(file1), get_cluster_size(file2))

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        offset = 0

        while True:
            buffer1 = f1.read(buffer_size)
            buffer2 = f2.read(buffer_size)

            if not buffer1 and not buffer2:
                print_verbose1("identical")
                return True

            if buffer1 != buffer2:
                for i in range(min(len(buffer1), len(buffer2))):
                    if buffer1[i] != buffer2[i]:
                        print_verbose1(f"difference found at offset {offset + i}")
                        return False

            offset += buffer_size


def execute_command_on_identical_files(group_hash: str, group: list[str]) -> None:
    """
    If user gave --exec argument, executes the given command with quotes space-separated file names as arguments.
    Return code if the command is ignored. Input and output/error are passed through.
    File names are sorted alphabetically.

    :param group_hash: Hash string for this group of files
    :param group: File names to give to the command
    """
    if ARGS.exec:
        hash_arg = group_hash + ' ' if ARGS.exec_hash_arg else ''
        cmdline = f"{ARGS.exec} {hash_arg}\"{'\" \"'.join(group)}\""
        print_verbose2(f"Executing '{cmdline}'")
        os.system(cmdline)


def round_file_size(file_name: str, file_size: int) -> int:
    """
    Rounds file size up to cluster size for a given name. If no cluster size information available, returns
    file_size.

    :param file_name: File name
    :param file_size: File size to round
    :return: Rounded or original file size
    """
    cluster_size = get_cluster_size(file_name)
    return math.ceil(file_size / cluster_size) * cluster_size if cluster_size else file_size


def get_cluster_size(file_name: str) -> [int, None]:
    """
    Tries to find cluster size for a given file. Cluster sizes are stored per path given in the arguments.
    If the cluster size cannot be found, returns None.

    :param file_name: File name to search for the cluster size
    :return: None or cluster size
    """
    for path, cluster_size in CLUSTER_SIZE_BY_PATH.items():
        if file_name.startswith(path):
            return cluster_size

    return None


def print_normal(*args, **kwargs) -> None:
    """
    Prints normal line, if no quiet argument given to the program. See print() for arguments.
    """
    if not ARGS.quiet:
        print(*args, **kwargs)


def print_verbose1(*args, **kwargs) -> None:
    """
    Prints verbose line if verbosity level 1 is enabled in program arguments. See print() for arguments.
    """
    if not ARGS.quiet and ARGS.verbose >= 1:
        print(*args, **kwargs)


def print_verbose2(*args, **kwargs) -> None:
    """
    Prints verbose line if verbosity level 2 is enabled in program arguments. See print() for arguments.
    """
    if not ARGS.quiet and ARGS.verbose >= 2:
        print(*args, **kwargs)


def print_verbose3(*args, **kwargs) -> None:
    """
    Prints verbose line if verbosity level 3 is enabled in program arguments. See print() for arguments.
    """
    if not ARGS.quiet and ARGS.verbose >= 3:
        print(*args, **kwargs)


def print_summary(*args, **kwargs) -> None:
    """
    Prints summary if summary printing is enabled in program arguments. See print() for arguments.
    """
    if not ARGS.quiet and not ARGS.no_summary:
        print(*args, **kwargs)


def fs_cluster_size(path: str) -> int:
    """
    Tries to obtain cluster size for a filesystem path, if possible.
    FIXME: Windows part is not tested yet.

    :param path: Path to obtain filesystem cluster size
    :return: Cluster size in bytes
    """
    if platform.system() == "Windows":
        import ctypes

        sectors_per_cluster = ctypes.c_ulonglong(0)
        bytes_per_sector = ctypes.c_ulonglong(0)
        free_clusters = ctypes.c_ulonglong(0)
        total_clusters = ctypes.c_ulonglong(0)

        result = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(path),
            ctypes.pointer(sectors_per_cluster),
            ctypes.pointer(bytes_per_sector),
            ctypes.pointer(free_clusters),
            ctypes.pointer(total_clusters),
        )

        if result == 0:
            raise ctypes.WinError()

        return sectors_per_cluster.value * bytes_per_sector.value
    else:
        statvfs = os.statvfs(path)
        return statvfs.f_bsize


def process_args() -> argparse.Namespace:
    """
    Processes program arguments and prints help if needed. Exits the process if no paths to scan given.

    :return: Parsed arguments
    """
    p = argparse.ArgumentParser(prog=PROG_NAME, description=
        "Finds file duplicates by comparing sizes, hashes of file prefixes, and/or hashes of "
        "the full file contents. The program calculates both CRC32 and MMH3 hashes minimize hash collisions. "
        "The wasted space is rounded up to the file system cluster size if the script is able "
        "to obtain this info from OS. ")
    p.add_argument('-q', '--quiet', action='store_true', default=False, help=
        "don't print even duplicate file names and summary. Useful for -e option")
    p.add_argument('-v', '--verbose', action='count', default=0, help=
        'verbosity level 1-3 (-v, -vv, -vvv)')
    p.add_argument('-S', '--no-summary', action="store_true", help=
        "don't print summary about wasted space")
    p.add_argument('-d', '--paranoid', action='store_true', default=False, help=
        "don't trust those hashes. Compare files byte-by-byte in a hardcode way, if size and hashes match. "
        "Can significantly increase execution time")
    p.add_argument('-e', '--exec', help=
        "execute a command for each group of identical files")
    p.add_argument('-a', '--exec-hash-arg', action='store_true', help=
        "include hash as the first argument in -e command (useless without -e)")
    p.add_argument('-m', '--min-file-size', default=4, type=int, help=
        'minimum file size to include into analysis. Default is 4 bytes')
    p.add_argument('-p', '--prefix-size', default=1024, type=int, help=
        'size of prefix in prefix comparison: if checksums of the prefix are different, the complete file comparison '
        'is skipped. Default is 1024 bytes')
    p.add_argument('-i', '--paths', dest='paths_file',
        type=argparse.FileType('r'), help=
        "read directory names from a file or the standard input, if '-' is given. ")
    p.add_argument('-V', '--version', action='version',
       version="%(prog)s " + PROG_VERSION + ". " + COPYRIGHT)

    # Internal, testing: Mock all prefix file hashes
    p.add_argument("--mock-prefix-hash", help=argparse.SUPPRESS)
    # Internal, testing: Mock all full file hashes
    p.add_argument("--mock-full-hash", help=argparse.SUPPRESS)

    p.add_argument("paths", nargs="*", help=
        "one or more directory names where to search for files recursively")

    if len(sys.argv) == 0:
        p.print_help()
        exit(0)

    args = p.parse_args()

    if not args.paths_file and len(args.paths) == 0:
        p.print_help()
        exit(1)

    verify_arguments(args)

    return args


def verify_arguments(args: argparse.Namespace) -> None:
    """
    Verifies parsed program arguments and prints warnings if needed

    :param args: Parsed program arguments
    """
    if args.quiet and args.verbose > 0:
        print("INFO: both -q and -v is given, but I choose to be quiet from now on")

    if args.min_file_size <= 0:
        print_verbose1(f"INFO: --min-file-size={args.min_file_size} does not make any sense, but it is up to you")

    if args.prefix_size <= 0:
        print_verbose1(f"INFO: --prefix-size={args.prefix_size} does not make any sense, but it is up to you")

    if args.exec_hash_arg and not args.exec:
        print_verbose1("INFO: --exec-hash-arg is given, but will be ignored, since no --exec is provided")

    if args.paths_file and args.paths:
        print_verbose1("INFO: Directories supplied in both --paths option and as program arguments. Will scan all of them")


if __name__ == '__main__':
    main()
