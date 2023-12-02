#!/usr/bin/env python3

"""This script takes a directory as input and produces a CBZ file as output.

Given a directory with images, it first checks all images for supported formats and possible corruption. The images are
then renamed (optionally) and packed into a zip/cbz file. If specified the original image files and directory are
deleted.
"""

import argparse
import os
import zipfile

import rich.markup
from PIL import Image
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn

# Define supported formats and exclusion list.
SUPPORTED_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']
EXTENSIONS = {'JPEG': '.jpg', 'PNG': '.png', 'GIF': '.gif', 'WEBP': '.webp'}
EXCLUDED_FILES = ['ComicInfo.xml']

# Create rich console.
RICH_CONSOLE = Console(highlight=False)


def check_files(files: list[str]) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    """Check all files and return supported image files, non-supported files and excluded files.

    Parameters
    ----------
    files : list[str]
        List of files.

    Returns
    -------
    img_files : list[tuple[str, str]]
        List of all supported image files and their formats.
    bad_files : list[str]
        List of unsupported files.
    excluded_files : list[str]
        List of files excluded from check.
    """
    img_files: list[tuple[str, str]] = []
    bad_files: list[str] = []
    excluded_files: list[str] = []
    with Progress(
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        MofNCompleteColumn(),
    ) as pbar:
        task = pbar.add_task('Checking files', total=len(files))
        for file in files:
            # If file name is in exclusion list do not check it.
            if os.path.basename(file) in EXCLUDED_FILES:
                excluded_files.append(file)
                pbar.update(task, advance=1)
                continue

            # Try opening the file as an image. If it does not give any errors check format, else mark it as a bad file.
            try:
                with Image.open(file, 'r') as im:
                    im.load()  # Detect possible corruptions.
                    if im.format not in SUPPORTED_FORMATS:
                        bad_files.append(file)
                    else:
                        img_files.append((file, im.format))
            except IOError:
                bad_files.append(file)

            pbar.update(task, advance=1)

    return img_files, bad_files, excluded_files


def make_cbz(dir: str, no_rename: bool = False, delete: bool = False) -> None:
    """Make a cbz from a directory.

    dir : str
        Path to directory.
    no_rename : bool, optional
        Don't rename files if True. (default=False)
    delete : bool, optional
        Delete original files and directory if True. (default=False)
    """
    # Check if output file is already present.
    out_file = f'{os.path.normpath(dir)}.cbz'
    if os.path.exists(out_file):
        RICH_CONSOLE.print(
            f"[bright_yellow]WARNING:[/bright_yellow] Output file already exists. Overwrite? {rich.markup.escape('[y/N]')} ", end='')
        choice = input('')
        if choice not in ['y', 'Y']:
            print('Not creating cbz.')
            return

    # Get all files and check if they are supported or not
    files = [os.path.join(dir, f) for f in sorted(os.listdir(dir))]
    img_files, bad_files, excluded_files = check_files(files)

    # Sanity check.
    assert len(img_files) + len(bad_files) + \
        len(excluded_files) == len(files), 'Image, bad and excluded files do add up to all files.'

    # If unsupported files are present report them and return.
    if len(bad_files) > 0:
        print(f'Found {len(bad_files)} unsupported files.')
        for file in bad_files:
            print(f'\t{os.path.basename(file)}')
        return

    # Create cbz file.
    print('Creating cbz ...')
    rename_format = '{:0' + str(max(2, len(str(len(img_files))))) + 'd}'
    with zipfile.ZipFile(out_file, 'w', compression=zipfile.ZIP_STORED) as zf:
        # Add image files.
        for idx, (file, format) in enumerate(img_files):
            if no_rename:
                arcname = os.path.basename(file)
            else:
                arcname = rename_format.format(idx+1) + EXTENSIONS[format]

            zf.write(file, arcname=arcname)

        # Add excluded files.
        for file in excluded_files:
            zf.write(file, os.path.basename(file))

    # If requested, delete original files and directory.
    if delete:
        print('Deleting original files and directory ...')
        for file in files:
            os.remove(file)
        os.rmdir(dir)


def main() -> None:
    """Main function for the script which takes directories as input and converts them to CBZs."""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', help='Directory(s) containing the images', nargs='+')
    parser.add_argument('-n', '--no_rename', help="Don't rename files", action='store_true')
    parser.add_argument('-d', '--delete', help='Delete original files', action='store_true')
    args = parser.parse_args()

    # Run make_cbz for each directory.
    for dir in args.dirs:
        # Normalize and ensure directory exists before calling make_cbz.
        dir = os.path.normpath(dir)
        if not os.path.exists(dir):
            RICH_CONSOLE.print(f'[bright_red]ERROR:[/bright_red] {rich.markup.escape(dir)} does not exist.')
            continue
        print(f'Processing {dir} ...')
        make_cbz(dir, args.no_rename, args.delete)


if __name__ == '__main__':
    main()
