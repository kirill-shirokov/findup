# findup

A simple utility for finding duplicate files. Requires Python 3.8+

Usage: 

```
usage: findup [-h] [-V] [-q] [-v] [-S] [-d] [-o OUTPUT] [-s SORT_OUTPUT]
              [-g SORT_GROUP] [-f OUTPUT_FORMAT] [-e EXEC] [-a EXEC_FORMAT]
              [-m MIN_FILE_SIZE] [-b PREFIX_SIZE] [-x EXCLUDE] [-i INCLUDE]
              [-X EXCLUDE_DIR] [-I INCLUDE_DIR] [-L] [-@] [-p PATHS_FILE]
              [paths ...]

Finds file duplicates by comparing sizes, hashes of file prefixes, hashes of
the full file contents and optionally the binary contents themselves. The
program calculates both CRC32 and MMH3 hashes minimize hash collisions. The
wasted space is rounded up to the file system cluster size if the script is
able to obtain this info from OS.

positional arguments:
  paths                 one or more file or directory names where to search
                        for files recursively

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -q, --quiet           don't print even duplicate file names and summary.
                        Useful for -e option
  -v, --verbose         verbosity level 1-3 (-v, -vv, -vvv)
  -S, --no-summary      don't print summary about wasted space
  -d, --dup-dirs        after scanning files identify duplicate directories
                        (where all files are duplicates to files in another
                        directory, after filtering with -i/-I/-x/-X)
  -o, --output OUTPUT   output report to a file. Verbose messages and errors
                        are still written to stdout/stderr. -q option
                        suppresses the output
  -s, --sort-output SORT_OUTPUT
                        comma-separated list of fields to sort the results:
                        name, path, size, wasted, mtime, Mtime, ctime, Ctime.
                        Prefixing field with '~' reverses the order. <size> is
                        the file size, <wasted> is the total wasted disk space
                        for the current duplicates group. <name> is just file
                        name of the first file in the group, <path> is full
                        path of the first file.
                        <ctime>/<Ctime>/<mtime>/Mtime>: lower case letter
                        chooses minimal time in duplicates group, while the
                        upper case uses maximal time.
  -g, --sort-group SORT_GROUP
                        comma-separated list of fields to sort the file names
                        within duplicates group: name, path, mtime, ctime.
                        Please see -s option above for explanation. This
                        option DOES impact order of files in -e. If not
                        specified, files are sorted by path.
  -f, --output-format OUTPUT_FORMAT
                        Output format as str.format() string. Variables:
                        {files}, {file_size}, {file_size_h},
                        {wasted_disk_space}, {wasted_disk_space_h}. _h suffix
                        is for human-readable sizes
  -e, --exec EXEC       execute a command for each group of identical files
  -a, --exec-format EXEC_FORMAT
                        argument format for -e command (useless without -e).
                        Default is '{cmd} {files}', but you can also add
                        {hash} and {file_size}
  -m, --min-file-size MIN_FILE_SIZE
                        minimum file size to include into analysis. Default is
                        4 bytes
  -b, --prefix-size PREFIX_SIZE
                        size of prefix in prefix comparison: if checksums of
                        the prefix are different, the complete file comparison
                        is skipped. Default is 1024 bytes
  -x, --exclude EXCLUDE
                        exclude files based on glob pattern or regexp (if
                        prefixed with 're:'). You can pass multiple -x
                        arguments
  -i, --include INCLUDE
                        only include files based on glob pattern or regexp (if
                        prefixed with 're:'). You can pass multiple -i
                        arguments. Processed after -x
  -X, --exclude-dir EXCLUDE_DIR
                        exclude directories (full paths) based on glob pattern
                        or regexp (if prefixed with 're:'). You can pass
                        multiple -X arguments
  -I, --include-dir INCLUDE_DIR
                        only include directories (full paths) based on glob
                        pattern or regexp (if prefixed with 're:'). You can
                        pass multiple -I arguments. Processed after -X
  -L, --no-follow-symlinks
                        don't follow symlinks
  -@, --paranoid        don't trust those hashes. Compare files byte-by-byte
                        in a hardcode way, if size and hashes match. Can
                        significantly increase execution time
  -p, --paths PATHS_FILE
                        read directory/file names from a file or the standard
                        input, if '-' is given.

Copyright (c) Kirill Shirokov, 2022-2025
```

## History

findup was written to find duplicate images on my disk in 2022 and made into a complete project in 2025, 
because I wanted to have full-fledged demo projects on GitHub for potential employers.

## Author

Kirill Shirokov

- Email: [kirill.shirokov@gmail.com](mailto:kirill.shirokov@gmail.com)
- Github: [https://github.com/kirill-shirokov/findup](https://github.com/kirill-shirokov/findup)
- LinkedIn: [https://www.linkedin.com/in/kirill-shirokov](https://www.linkedin.com/in/kirill-shirokov/)
