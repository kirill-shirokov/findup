# findup

A simple utility for finding duplicate files. Requires Python 3.

```
usage: findup [-h] [-q] [-v] [-S] [-d] [-e EXEC] [-a] [-m MIN_FILE_SIZE]
              [-p PREFIX_SIZE] [-i PATHS_FILE] [-V]
              [paths ...]

Finds file duplicates by comparing sizes, hashes of file prefixes, and/or hashes of
the full file contents. The program calculates both CRC32 and MMH3 hashes minimize
hash collisions. The wasted space is rounded up to the file system cluster size if
the script is able to obtain this info from OS.

positional arguments:
  paths                 one or more directory names where to search for files
                        recursively

options:
  -h, --help            show this help message and exit
  -q, --quiet           don't print even duplicate file names and summary. Useful
                        for -e option
  -v, --verbose         verbosity level 1-3 (-v, -vv, -vvv)
  -S, --no-summary      don't print summary about wasted space
  -d, --paranoid        don't trust those hashes. Compare files byte-by-byte in a
                        hardcode way, if size and hashes match. Can significantly
                        increase execution time
  -e, --exec EXEC       execute a command for each group of identical files
  -a, --exec-hash-arg   include hash as the first argument in -e command (useless
                        without -e)
  -m, --min-file-size MIN_FILE_SIZE
                        minimum file size to include into analysis. Default is 4
                        bytes
  -p, --prefix-size PREFIX_SIZE
                        size of prefix in prefix comparison: if checksums of the
                        prefix are different, the complete file comparison is
                        skipped. Default is 1024 bytes
  -i, --paths PATHS_FILE
                        read directory names from a file or the standard input, if
                        '-' is given.
  -V, --version         show program's version number and exit
```

## History

findup was written to find duplicate images on my disk in 2022 and made into a complete project in 2025, 
because I wanted to have full-fledged demo projects on GitHub for potential employers.

## Author

Kirill Shirokov

- Email: [kirill.shirokov@gmail.com](mailto:kirill.shirokov@gmail.com)
- LinkedIn: [https://www.linkedin.com/in/kirill-shirokov](https://www.linkedin.com/in/kirill-shirokov/)
