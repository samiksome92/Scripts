#!/usr/bin/env python3

"""This script takes a directory as input and shows all images inside it as a gallery.

The script scans a given directory for supported image files. It then generates HTML pages for a gallery populated with
found images. Once the HTML files have been created, the gallery is shown using the default web browser. Supports
keyboard and mouse navigation.
"""

import argparse
import os
import platform
import random
import re
import subprocess
from typing import List, Union

from PIL import Image
from tqdm import tqdm

SUPPORTED_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']
ID_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# Command to open default browser in Windows and Linux.
system = platform.system()
if system == 'Windows':
    BROWSER = ['explorer']
elif system == 'Linux':
    BROWSER = ['xdg-open']


def is_supported_img(file_path: str) -> bool:
    """Checks if a file is a supported image or not.

    Parameters
    ----------
    file_path : str
        Path to the file.

    Returns
    -------
    bool
        True if supported image, False otherwise.
    """
    try:
        with Image.open(file_path, 'r') as img:
            if img.format in SUPPORTED_FORMATS:
                return True
            return False
    except IOError:
        return False


def get_img_files(dir_path: str) -> List[str]:
    """Returns a list of images under the given directory.

    Parameters
    ----------
    dir_path : str
        Directory to scan.

    Returns
    -------
    img_files : List[str]
        List of images.
    """
    # Get list of all files in directory.
    file_list = [os.path.join(dir_path, f) for f in sorted(os.listdir(dir_path))]

    # Check all files to filter out valid images.
    img_files = []
    progress_bar = tqdm(file_list, bar_format='Checking all files |{bar:20}| {n_fmt}/{total_fmt}')
    for file_path in progress_bar:
        if is_supported_img(file_path):
            img_files.append(file_path)
    return img_files


def randomize_imgs(img_files: List[str]) -> List[str]:
    """Randomize the order of images while keeping multi-part images together.

    Parameters
    ----------
    img_files : List[str]
        List of images.

    Returns
    -------
    img_files : List[str]
        Randomized list of images.
    """
    # Group image sequences.
    img_file_groups = {}
    for img_file in img_files:
        img_name = re.sub('\s[0-9]*$', '', os.path.splitext(os.path.basename(img_file))[0])
        if img_name not in img_file_groups:
            img_file_groups[img_name] = []
        img_file_groups[img_name].append(img_file)

    # Shuffle and return randomized list.
    img_keys = list(img_file_groups.keys())
    random.shuffle(img_keys)
    img_files = []
    for img_key in img_keys:
        for img_file in img_file_groups[img_key]:
            img_files.append(img_file)

    return img_files


def write_img_html(out_file: str, img_file: str, prev: str, next: str) -> None:
    """Writes out the html for a single image file.

    Parameters
    ----------
    out_file : str
        Output HTML file.
    img_file : str
        Image file.
    prev : str
        Previous image in gallery.
    next : str
        Next image in gallery.
    """
    # HTML start.
    html = (
        '<!DOCTYPE html>'
        '<html style="width: 100%; height: 100%;">'
        '<head>'
        '<title>Gallery</title>'
        '<meta charset="utf-8">'
    )

    # CSS section.
    html += (
        '<style>'
        'html {'
        '   margin: 0;'
        '   width: 100%;'
        '   height: 100%;'
        '}'
        'body {'
        '   display: flex;'
        '   justify-content: center;'
        '   align-items: center;'
        '   margin: 0;'
        '   width: 100%;'
        '   height: 100%;'
        '   background-color: #212121;'
        '}'
        '.image {'
        '   position: absolute;'
        '   max-width: 100%;'
        '   max-height: 100%;'
        '   object-fit: scale-down;'
        '}'
        '</style>'
    )

    # HTML body.
    html += (
        '</head>'
        '<body id="body">'
        f'<img src="file://{img_file}" class="image" id="image">'
    )

    # JavaScript section.
    html += (
        '<script>'
        'const body = document.getElementById("body");'
        'const img = document.getElementById("image");'
        'document.addEventListener("keydown", (event) => {'
        '   if (event.key === "+") {'
        '       const neww = img.offsetWidth * 1.05;'
        '       const newh = img.offsetHeight * 1.05;'
        '       const imageCss = document.styleSheets[0].cssRules[2].style;'
        '       imageCss.removeProperty("max-width");'
        '       imageCss.removeProperty("max-height");'
        '       imageCss.setProperty("width", neww.toString()+"px");'
        '       imageCss.setProperty("height", newh.toString()+"px");'
        '       imageCss.setProperty("object-fit", "contain");'
        '   }'
        '   else if (event.key === "-") {'
        '       const neww = img.offsetWidth * 0.95;'
        '       const newh = img.offsetHeight * 0.95;'
        '       const imageCss = document.styleSheets[0].cssRules[2].style;'
        '       imageCss.removeProperty("max-width");'
        '       imageCss.removeProperty("max-height");'
        '       imageCss.setProperty("width", neww.toString()+"px");'
        '       imageCss.setProperty("height", newh.toString()+"px");'
        '       imageCss.setProperty("object-fit", "contain");'
        '   }'
        '   else if (event.key === "0") {'
        '       const imageCss = document.styleSheets[0].cssRules[2].style;'
        '       imageCss.removeProperty("width");'
        '       imageCss.removeProperty("height");'
        '       imageCss.setProperty("max-width", "100%");'
        '       imageCss.setProperty("max-height", "100%");'
        '       imageCss.setProperty("object-fit", "scale-down");'
        '   }'
        '   else if (event.key === "ArrowLeft" && img.offsetWidth <= body.offsetWidth && img.offsetHeight <= body.offsetHeight)'
        f'      window.location.replace("{prev}");'
        '   else if (event.key === "ArrowRight" && img.offsetWidth <= body.offsetWidth && img.offsetHeight <= body.offsetHeight)'
        f'      window.location.replace("{next}");'
        '   else if (event.key === "Backspace" || event.key === "Escape")'
        '       history.back();'
        '   else if (event.key === "q")'
        '       window.close();'
        '}, false);'
        '</script>'
    )

    # End HTML.
    html += (
        '</body>'
        '</html>'
    )

    with open(out_file, 'w', encoding='utf8') as file_obj:
        file_obj.write(html)


def write_html(out_file: str, img_files: List[str], img_ids: List[str], height: int = 300, padding: int = 5) -> None:
    """Writes out the html for the gallery itself.

    Parameters
    ----------
    out_file : str
        Output HTML file.
    img_files : List[str]
        List of images.
    img_ids : List[str]
        IDs of images.
    height : int, optional
        Height of each row. (default=300)
    padding : int, optional
        Padding between items. (default=5)
    """
    # HTML start.
    html = (
        '<!DOCTYPE html>'
        '<html>'
        '<head>'
        '<title>Gallery</title>'
        '<meta charset="utf-8">'
    )

    # CSS section.
    html += (
        '<style>'
        'body {'
        '   display: flex;'
        '   flex-wrap: wrap;'
        f'  margin: {padding}px;'
        '   background-color: #212121;'
        '}'
        '.img {'
        f'  height: {height}px;'
        f'  margin: {padding}px;'
        '   flex-grow: 1;'
        '   object-fit: cover;'
        '   box-sizing: border-box;'
        '}'
        '.selected {'
        '   border: 1px dashed #fafafa;'
        '}'
        '</style>'
    )

    # End head section.
    html += (
        '</head>'
        f'<body>'
    )

    # Images.
    for idx, img_file in enumerate(img_files):
        title = os.path.splitext(os.path.basename(img_file))[0]
        html += (
            f'<img src="file://{img_file}" title="{title}" class="img" id="{img_ids[idx]}">'
        )
    html += '<div style="flex-grow: 1e10;"></div>'

    # JavaScript section.
    html += (
        '<script>'
        'function visible(element) {'
        '   const rect = element.getBoundingClientRect();'
        '   return rect.top >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight);'
        '}'
        'let selected = -1;'
        'const imgs = document.getElementsByClassName("img");'
        'Array.from(imgs).forEach((img, i) => {'
        '   img.addEventListener("click", (event) => {'
        '       if (selected != -1 && selected != i) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected = -1;'
        '       }'
        '       window.location.href = img.id+".html";'
        '   }, false);'
        '});'
        'document.addEventListener("keydown", (event) => {'
        '   if (event.key === "ArrowLeft") {'
        '       if (selected === -1) {'
        '           for (i = 0; i<imgs.length; i++) {'
        '               if (visible(imgs[i])) {'
        '                   selected = i;'
        '                   imgs[selected].classList.add("selected");'
        '                   imgs[selected].scrollIntoView({"behavior": "smooth", "block": "nearest", "inline":"nearest"});'
        '                   break;'
        '               }'
        '           }'
        '       }'
        '       else if (selected > 0) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected -= 1;'
        '           imgs[selected].classList.add("selected");'
        '           imgs[selected].scrollIntoView({"behavior": "smooth", "block": "nearest", "inline":"nearest"});'
        '       }'
        '   }'
        '   else if (event.key === "ArrowRight") {'
        '       if (selected === -1) {'
        '           for (i = 0; i<imgs.length; i++) {'
        '               if (visible(imgs[i])) {'
        '                   selected = i;'
        '                   imgs[selected].classList.add("selected");'
        '                   imgs[selected].scrollIntoView({"behavior": "smooth", "block": "nearest", "inline":"nearest"});'
        '                   break;'
        '               }'
        '           }'
        '       }'
        '       else if (selected < imgs.length - 1) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected += 1;'
        '           imgs[selected].classList.add("selected");'
        '           imgs[selected].scrollIntoView({"behavior": "smooth", "block": "nearest", "inline":"nearest"});'
        '       }'
        '   }'
        '   else if (event.key === "ArrowUp") {'
        '       if (selected !== -1) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected = -1;'
        '       }'
        '   }'
        '   else if (event.key === "ArrowDown") {'
        '       if (selected !== -1) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected = -1;'
        '       }'
        '   }'
        '   else if (event.key === "Enter" && selected !== -1)'
        '       imgs[selected].click();'
        '   else if (event.key === "q")'
        '       window.close();'
        '}, false);'
        '</script>'
    )

    # End HTML.
    html += (
        '</body>'
        '</html>'
    )

    with open(out_file, 'w', encoding='utf8') as file_obj:
        file_obj.write(html)


def create_gallery(dir_path: str, randomize: bool = False, height: int = 300, padding: int = 5) -> Union[str, None]:
    """Given a directory scan it for images and create a gallery for the same.

    Parameters
    ----------
    dir_path : str
        Directory path.
    randomize : bool, optional
        Randomize order of images. (default=False)
    height : int, optional
        Height of each row. (default=300)
    padding : int, optional
        Padding between images. (default=5)

    Returns
    -------
    str | None
        Path to gallery HTML or None if there were no images in directory.
    """
    # Create directories to store the html files.
    system = platform.system()
    if system == 'Windows':
        out_dir = os.path.join(os.environ['LOCALAPPDATA'], 'gallery.py')  # Use AppData\Local in Windows.
    elif system == 'Linux':
        out_dir = os.path.join(os.environ['HOME'], '.local', 'share', 'gallery.py')  # Use .local/share in Linux.
    os.makedirs(out_dir, exist_ok=True)

    # Get all images.
    img_files = get_img_files(dir_path)

    # If no images are found return None.
    if len(img_files) == 0:
        return None

    # Randomize images if needed.
    if randomize:
        img_files = randomize_imgs(img_files)

    # Create ids for images.
    img_ids = []
    for _ in img_files:
        img_id = ''.join(random.choices(ID_ALPHABET, k=32))
        while img_id in img_ids:
            img_id = ''.join(random.choices(ID_ALPHABET, k=32))
        img_ids.append(img_id)

    # Clear old html files.
    old_files = [os.path.join(out_dir, f) for f in os.listdir(out_dir)]
    for old_file in old_files:
        os.remove(old_file)

    # Write out htmls for gallery and images.
    write_html(os.path.join(out_dir, 'index.html'), img_files, img_ids, height, padding)
    for idx, img_file in enumerate(img_files):
        prev_idx = idx - 1
        next_idx = idx + 1
        if idx == 0:
            prev_idx = len(img_files) - 1
        if idx == len(img_files) - 1:
            next_idx = 0
        write_img_html(
            os.path.join(out_dir, f'{img_ids[idx]}.html'),
            img_file,
            f'{img_ids[prev_idx]}.html',
            f'{img_ids[next_idx]}.html'
        )
    return os.path.join(out_dir, 'index.html')


def open_gallery(html_path: str, browser: List[str] = BROWSER) -> None:
    """Given a path open it in the browser.

    Parameters
    ----------
    html_path : str
        Path to HTML file.
    browser : List[str]
        Command line for browser.
    """
    subprocess.run(browser + [html_path])


def main() -> None:
    """Main function for the script"""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_path', help='Directory containing the images')
    parser.add_argument('-r', '--randomize', help='Randomize the order of the images', action='store_true')
    parser.add_argument('-t', '--height', help='Height of each row in pixels', type=int, default=300)
    parser.add_argument('-p', '--padding', help='Padding between images', type=int, default=5)
    parser.add_argument('-b', '--browser', help='Custom browser command (arguments supported)',
                        nargs=argparse.REMAINDER)
    args = parser.parse_args()

    # Use normalized absolute path internally.
    args.dir_path = os.path.normpath(os.path.abspath(args.dir_path))

    # If browser command is not provided use default.
    if args.browser is None:
        args.browser = BROWSER

    # Create gallery and then open it.
    html_path = create_gallery(args.dir_path, args.randomize, args.height, args.padding)
    if html_path:
        open_gallery(html_path, args.browser)
    else:
        print('No images were found in the directory.')


if __name__ == '__main__':
    main()
