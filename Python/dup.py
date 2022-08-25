#!/usr/bin/env python3

"""Check for and remove duplicate files.

Checks for duplicate files in given directories using size comparison, hashing, and byte-by-byte comparison. By default
it removes all duplicates it finds and outputs a list of deleted files. It can also be used to simply output the list of
duplicates without deleting them.
"""

import argparse
import filecmp
import os
from typing import Dict, List, Tuple
import zlib

from tabulate import tabulate
from tqdm import tqdm


def crc32(file: str, chunk_size: int = 65536) -> str:
    """Compute CRC32 checksum of a file using chunking.

    Parameters
    ----------
    file : str
        File path.
    chunk_size : int
        Chunk size in bytes. (default=65536)

    Returns
    -------
    checksum : str
        CRC32 checksum as hex string.
    """
    checksum = 0
    with open(file, 'rb') as file_obj:
        while True:
            data = file_obj.read(chunk_size)
            if not data:
                break

            checksum = zlib.crc32(data, checksum)
    checksum = hex(checksum)[2:]

    return checksum


def find_dups(dirs: List[str], no_hash: bool = False) -> List[Tuple[str, str]]:
    """Check for duplicate files.

    Parameters
    ----------
    dirs : List[str]
        Directories to search.
    no_hash : bool, optional
        Don't use hashing. (default=False)

    Returns
    -------
    dup_files : List[Tuple[str, str]]
        List of duplicates found.
    """
    dup_files: List[str] = []

    # Get list of all files.
    print('Getting list of files.')
    files = []
    for dir in dirs:
        files += sorted([os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))])
    print(f'Found {len(files)} files across directories.')

    # Check file sizes.
    print('Checking file sizes.')
    size2files: Dict[int, List[str]] = {}
    for file in files:
        size = os.stat(file).st_size
        if size not in size2files:
            size2files[size] = []
        size2files[size].append(file)

    # Find duplicates.
    progress_bar = tqdm(total=len(files), bar_format='Finding duplicates |{bar:20}| {n_fmt}/{total_fmt}')
    for size, files in size2files.items():
        if len(files) == 1:  # If only 1 file is present skip it as it has no duplicate.
            progress_bar.update(1)
            continue

        if no_hash:
            # If not computing hashes, we can directly start comparing files byte by byte.
            unique_files = [files[0]]
            for file in files[1:]:
                for oldfile in unique_files:
                    if filecmp.cmp(oldfile, file, shallow=False):
                        dup_files.append((file, oldfile))
                        break
                else:
                    unique_files.append(file)
        else:
            # First compute hashes and only compare byte by byte if checksum matches.
            hash2files: Dict[str, List[str]] = {}
            for file in files:
                # Compute CRC32 checksum. Since we'll do byte-by-byte comparisons if checksums match, using CRC32 is fine.
                checksum = crc32(file)

                # If checksum is already present compare against earlier files and see if it matches any.
                if checksum in hash2files:
                    for oldfile in hash2files[checksum]:
                        if filecmp.cmp(oldfile, file, shallow=False):
                            dup_files.append((file, oldfile))
                            break
                    else:
                        hash2files[checksum].append(file)  # Did not match any file. Hash collision. Add to list.
                else:
                    hash2files[checksum] = [file]
        progress_bar.update(len(files))
    progress_bar.close()

    return dup_files


def main() -> None:
    """Main function for the script."""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', help='Directories to search', nargs='+')
    parser.add_argument('-f', '--find', help="Only find duplicates. Don't delete them", action='store_true')
    parser.add_argument('-n', '--no_hash', help="Don't use any hashing", action='store_true')
    parser.add_argument('-o', '--output', help='Output file with list of duplicates', default=None)
    args = parser.parse_args()

    # Get duplicates.
    dup_files = find_dups(args.dirs, args.no_hash)

    if len(dup_files) == 0:
        print('No duplicates found.')
        return

    # If --find is not given delete the duplicates.
    if not args.find:
        print('Removing duplicates ...')
        print(tabulate([(os.path.normpath(a), os.path.normpath(b))
              for a, b in dup_files], headers=['Duplicate File', 'Matched To']))
        for dup_file, _ in dup_files:
            os.remove(dup_file)
        print(f'Removed {len(dup_files)} duplicates.')
    else:
        print(f'Found {len(dup_files)} duplicates ...')
        print(tabulate([(os.path.normpath(a), os.path.normpath(b))
              for a, b in dup_files], headers=['Duplicate File', 'Matched To']))

    # Write output file is --output is provided.
    if args.output:
        with open(args.output, 'w', encoding='utf8') as file_obj:
            for dup_file, old_file in dup_files:
                file_obj.write(f'{os.path.normpath(dup_file)}\t{os.path.normpath(old_file)}\n')


if __name__ == '__main__':
    main()
