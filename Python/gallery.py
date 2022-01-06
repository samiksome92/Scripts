#!/usr/bin/env python3

"""This script takes a directory as input and shows all images inside it as a gallery.

The script scans a given directory for supported image files. It then generate a HTML page for a gallery populated with
found images. Once the HTML file has been created, the gallery is shown using the default web browser. Supports keyboard
and mouse navigation.
"""

import argparse
import http.server
import os
import platform
import posixpath
import random
import re
import socket
import socketserver
import string
import subprocess
from typing import Any, Dict, List, Union
import urllib

from PIL import Image
from tqdm import tqdm

SUPPORTED_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']
ID_ALPHABET = string.ascii_letters + string.digits

# Command to open default browser in Windows and Linux.
SYSTEM = platform.system()
if SYSTEM == 'Windows':
    BROWSER = ['explorer']
elif SYSTEM == 'Linux':
    BROWSER = ['xdg-open']


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom http request handler.

    This class extends SimpleHTTPRequestHandler and adds support for absolute file paths by overriding translate_path.
    In order to do this it first considers the path to be relative. If the relative path exists then it is used,
    otherwise the absolute path is used.
    """

    def translate_path(self, path: str) -> str:
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = list(filter(None, words))

        # Relative path.
        rel_path = self.directory
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            rel_path = os.path.join(rel_path, word)

        # Absolute path.
        if SYSTEM == 'Windows':
            abs_path = words[0] if len(words) > 0 else ''
        elif SYSTEM == 'Linux':
            abs_path = '/'
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            abs_path = os.path.join(abs_path, word)

        # If relative path exists, use it, else use absolute path.
        if os.path.exists(rel_path):
            path = rel_path
        else:
            path = abs_path

        # Trailing slash seems to causing issues on Firefox, so it has been removed.
        return path


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


def get_img_info(file_path: str) -> Dict[str, Any]:
    """Returns a dictionary containing information about the image.

    Parameters
    ----------
    file_path : str
        Path to the file.

    Returns
    -------
    info : Dict[str, Any]
        Info dictionary.
    """
    info = {}
    with Image.open(file_path, 'r') as img:
        w, h = img.size
        info['w'] = w
        info['h'] = h

    return info


def get_img_files(dir_path: str) -> List[str]:
    """Returns a list of images under the given directory, along with their infos.

    Parameters
    ----------
    dir_path : str
        Directory to scan.

    Returns
    -------
    img_files : List[str]
        List of images.
    img_infos : Dict[str, Dict]
        Information about the images.
    """
    # Get list of all files in directory.
    file_list = [os.path.join(dir_path, f) for f in sorted(os.listdir(dir_path))]

    # Check all files to filter out valid images.
    img_files = []
    img_infos = {}
    progress_bar = tqdm(file_list, bar_format='Checking all files |{bar:20}| {n_fmt}/{total_fmt}')
    for file_path in progress_bar:
        if is_supported_img(file_path):
            img_files.append(file_path)
            img_infos[file_path] = get_img_info(file_path)
    return img_files, img_infos


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


def resize_imgs(img_files: List[str], img_ids: List[str], out_dir: str, height: int = 300) -> None:
    """Resize images and save them in provided directory.

    Parameters
    ----------
    img_files : List[str]
        List of images.
    img_ids : List[str]
        IDs of images.
    out_dir : str
        Output directory.
    height : int, optional
        Height to resize to. (default=300)
    """
    progress_bar = tqdm(
        zip(img_files, img_ids),
        bar_format='Resizing Images    |{bar:20}| {n_fmt}/{total_fmt}',
        total=len(img_files)
    )
    for img_file, img_id in progress_bar:
        with Image.open(img_file, 'r') as img:
            w, h = img.size
            nw = int(w/h*height)
            nh = height
            img = img.resize((nw, nh), resample=Image.BICUBIC)
            img.save(os.path.join(out_dir, img_id+'.png'))


def write_html(
    img_files: List[str],
    img_ids: List[str],
    img_infos: Dict[str, Dict],
    out_dir: str,
    height: int = 300,
    padding: int = 5,
    no_resize: bool = False,
    as_server: bool = False,
) -> None:
    """Writes out the html for the gallery.

    Parameters
    ----------
    img_files : List[str]
        List of images.
    img_ids : List[str]
        IDs of images.
    img_infos : Dict[str, Dict]
        Info about the images.
    out_dir : str
        Output directory.
    height : int, optional
        Height of each row. (default=300)
    padding : int, optional
        Padding between items. (default=5)
    no_resize : bool, optional
        Do not resize images for thumbnails if True. (default=False)
    as_server : bool, optional
        Run a http server instead of opening the HTML file directly. (default=False)
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
        'html, body {'
        '   margin: 0px;'
        '   width: 100%;'
        '   height: 100%;'
        '   background-color: #212121;'
        '}'
        '#gallery {'
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
        '#viewer {'
        '   display: none;'
        '   margin: 0px;'
        '   width: 100%;'
        '   height: 100%;'
        '}'
        '#viewerImg {'
        '   margin: auto;'
        '   max-width: 100%;'
        '   max-height: 100%;'
        '   object-fit: scale-down;'
        '   pointer-events: none;'
        '}'
        '#left {'
        '   position: fixed;'
        '   width: 100px;'
        '   height: 100%;'
        '}'
        '#right {'
        '   position: fixed;'
        '   right: 0;'
        '   width: 100px;'
        '   height: 100%;'
        '}'
        '</style>'
    )

    # End head section.
    html += (
        '</head>'
        f'<body><div id="gallery">'
    )

    # Image gallery.
    for img_file, img_id in zip(img_files, img_ids):
        title = os.path.splitext(os.path.basename(img_file))[0]
        img_url: str = urllib.parse.quote(img_file.replace('\\', '/')).replace('%3A', ':')
        info = img_infos[img_file]

        if as_server:
            img_url = 'http://127.0.0.1:8000/'+img_url
        else:
            img_url = 'file://'+img_url

        if no_resize:
            html += f'<img src="{img_url}" title="{title}" class="img" id="{img_id}" data-url="{img_url}" data-w="{info["w"]}" data-h="{info["h"]}">'
        else:
            html += f'<img src="{img_id}.png" title="{title}" class="img" id="{img_id}" data-url="{img_url}" data-w="{info["w"]}" data-h="{info["h"]}">'
    html += '<div style="flex-grow: 1e10;"></div></div>'

    # Image viewer.
    html += (
        '<div id="viewer">'
        '   <img id="viewerImg">'
        '   <div id="left"></div>'
        '   <div id="right"></div>'
        '</div>'
    )

    # JavaScript section.
    html += (
        '<script>'
        'function isVisible(element) {'
        '   const rect = element.getBoundingClientRect();'
        '   return rect.top >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight);'
        '}'
        'function getOverlap(element1, element2, direction) {'
        '   const rect1 = element1.getBoundingClientRect();'
        '   const rect2 = element2.getBoundingClientRect();'
        '   if (direction == "up" && rect1.top - rect2.bottom > 10)'
        '       return 0;'
        '   if (direction == "down" && rect2.top - rect1.bottom > 10)'
        '       return 0;'
        '   overlapBegin = rect1.left > rect2.left ? rect1.left : rect2.left;'
        '   overlapEnd = rect1.right < rect2.right ? rect1.right : rect2.right;'
        '   if (overlapBegin > overlapEnd)'
        '       return 0;'
        '   else'
        '       return overlapEnd - overlapBegin;'
        '}'
        'function selectLeft() {'
        '   if (selected === -1) {'
        '       for (i = imgs.length; i >= 0; i--)'
        '           if (isVisible(imgs[i])) {'
        '               selected = i;'
        '               imgs[selected].classList.add("selected");'
        '               imgs[selected].scrollIntoView({'
        '                   "behavior": "smooth",'
        '                   "block": "nearest",'
        '                   "inline": "nearest"'
        '               });'
        '               break;'
        '           }'
        '   } else if (selected > 0) {'
        '       imgs[selected].classList.remove("selected");'
        '       selected -= 1;'
        '       imgs[selected].classList.add("selected");'
        '       imgs[selected].scrollIntoView({'
        '           "behavior": "smooth",'
        '           "block": "nearest",'
        '           "inline": "nearest"'
        '       });'
        '   }'
        '}'
        'function selectRight() {'
        '   if (selected === -1) {'
        '       for (i = 0; i < imgs.length; i++)'
        '           if (isVisible(imgs[i])) {'
        '               selected = i;'
        '               imgs[selected].classList.add("selected");'
        '               imgs[selected].scrollIntoView({'
        '                   "behavior": "smooth",'
        '                   "block": "nearest",'
        '                   "inline": "nearest"'
        '               });'
        '               break;'
        '           }'
        '   } else if (selected < imgs.length - 1) {'
        '       imgs[selected].classList.remove("selected");'
        '       selected += 1;'
        '       imgs[selected].classList.add("selected");'
        '       imgs[selected].scrollIntoView({'
        '           "behavior": "smooth",'
        '           "block": "nearest",'
        '           "inline": "nearest"'
        '       });'
        '   }'
        '}'
        'function selectUp() {'
        '   if (selected === -1) {'
        '       for (i = imgs.length - 1; i >= 0; i--)'
        '           if (isVisible(imgs[i])) {'
        '               selected = i;'
        '               imgs[selected].classList.add("selected");'
        '               imgs[selected].scrollIntoView({'
        '                   "behavior": "smooth",'
        '                   "block": "nearest",'
        '                   "inline": "nearest"'
        '               });'
        '               break;'
        '           }'
        '   } else {'
        '       bestOverlap = 0;'
        '       bestOverlapIdx = -1;'
        '       for (i = selected - 1; i >= 0; i--) {'
        '           overlap = getOverlap(imgs[selected], imgs[i], "up");'
        '           if (overlap > bestOverlap) {'
        '               bestOverlap = overlap;'
        '               bestOverlapIdx = i;'
        '           }'
        '       }'
        '       if (bestOverlapIdx !== -1) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected = bestOverlapIdx;'
        '           imgs[selected].classList.add("selected");'
        '           imgs[selected].scrollIntoView({'
        '               "behavior": "smooth",'
        '               "block": "nearest",'
        '               "inline": "nearest"'
        '           });'
        '       }'
        '   }'
        '}'
        'function selectDown() {'
        '   if (selected === -1) {'
        '       for (i = 0; i < imgs.length; i++)'
        '           if (visible(imgs[i])) {'
        '               selected = i;'
        '               imgs[selected].classList.add("selected");'
        '               imgs[selected].scrollIntoView({'
        '                   "behavior": "smooth",'
        '                   "block": "nearest",'
        '                   "inline": "nearest"'
        '               });'
        '               break;'
        '           }'
        '   } else {'
        '       bestOverlap = 0;'
        '       bestOverlapIdx = -1;'
        '       for (i = selected + 1; i < imgs.length; i++) {'
        '           overlap = getOverlap(imgs[selected], imgs[i], "down");'
        '           if (overlap > bestOverlap) {'
        '               bestOverlap = overlap;'
        '               bestOverlapIdx = i;'
        '           }'
        '       }'
        '       if (bestOverlapIdx !== -1) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected = bestOverlapIdx;'
        '           imgs[selected].classList.add("selected");'
        '           imgs[selected].scrollIntoView({'
        '               "behavior": "smooth",'
        '               "block": "nearest",'
        '               "inline": "nearest"'
        '           });'
        '       }'
        '   }'
        '}'
        'function viewImg(idx) {'
        '   const img = imgs[idx];'
        '   viewerImg.setAttribute("src", img.dataset.url);'
        '   viewerImg.style.removeProperty("width");'
        '   viewerImg.style.removeProperty("height");'
        '   viewerImg.style.maxWidth = "100%";'
        '   viewerImg.style.maxHeight = "100%";'
        '   scrollPos = window.pageYOffset;'
        '   document.title = img.title;'
        '   gallery.style.display = "none";'
        '   viewer.style.display = "flex";'
        '   mode = "viewer";'
        '   viewerIdx = idx;'
        '}'
        'function zoomIn() {'
        '   const neww = viewerImg.offsetWidth * 1.05;'
        '   const newh = viewerImg.offsetHeight * 1.05;'
        '   viewerImg.style.width = neww.toString() + "px";'
        '   viewerImg.style.height = newh.toString() + "px";'
        '   viewerImg.style.maxWidth = neww.toString() + "px";'
        '   viewerImg.style.maxHeight = newh.toString() + "px";'
        '   viewerImg.style.objectFit = "contain";'
        '}'
        'function zoomOut() {'
        '   const neww=viewerImg.offsetWidth / 1.05;'
        '   const newh=viewerImg.offsetHeight / 1.05;'
        '   viewerImg.style.width=neww.toString() + "px";'
        '   viewerImg.style.height=newh.toString() + "px";'
        '   viewerImg.style.maxWidth=neww.toString() + "px";'
        '   viewerImg.style.maxHeight=newh.toString() + "px";'
        '   viewerImg.style.objectFit="contain";'
        '}'
        'function zoomFit() {'
        '   viewerImg.style.removeProperty("width");'
        '   viewerImg.style.removeProperty("height");'
        '   viewerImg.style.maxWidth="100%";'
        '   viewerImg.style.maxHeight="100%";'
        '   viewerImg.style.objectFit="scale-down";'
        '}'
        'function zoomFull() {'
        '   viewerImg.style.width=imgs[viewerIdx].dataset.w + "px";'
        '   viewerImg.style.height=imgs[viewerIdx].dataset.h + "px";'
        '   viewerImg.style.maxWidth=imgs[viewerIdx].dataset.w + "px";'
        '   viewerImg.style.maxHeight=imgs[viewerIdx].dataset.h + "px";'
        '   viewerImg.style.objectFit="contain";'
        '}'
        'function goLeft() {'
        '   if (viewerImg.offsetWidth <= document.body.offsetWidth && viewerImg.offsetHeight <= document.body.offsetHeight) {'
        '       if (viewerIdx > 0) {'
        '           viewerImg.setAttribute("src", imgs[viewerIdx - 1].dataset.url);'
        '           viewerIdx -= 1;'
        '       } else {'
        '           viewerImg.setAttribute("src", imgs[imgs.length - 1].dataset.url);'
        '           viewerIdx=imgs.length - 1;'
        '       }'
        '       viewerImg.style.removeProperty("width");'
        '       viewerImg.style.removeProperty("height");'
        '       viewerImg.style.maxWidth="100%";'
        '       viewerImg.style.maxHeight="100%";'
        '       document.title=imgs[viewerIdx].title;'
        '   }'
        '}'
        'function goRight() {'
        '   if (viewerImg.offsetWidth <= document.body.offsetWidth && viewerImg.offsetHeight <= document.body.offsetHeight) {'
        '       if (viewerIdx < imgs.length - 1) {'
        '           viewerImg.setAttribute("src", imgs[viewerIdx + 1].dataset.url);'
        '           viewerIdx += 1;'
        '       } else {'
        '           viewerImg.setAttribute("src", imgs[0].dataset.url);'
        '           viewerIdx=0;'
        '       }'
        '       viewerImg.style.removeProperty("width");'
        '       viewerImg.style.removeProperty("height");'
        '       viewerImg.style.maxWidth="100%";'
        '       viewerImg.style.maxHeight="100%";'
        '       document.title=imgs[viewerIdx].title;'
        '   }'
        '}'
        'function showGallery() {'
        '   viewer.style.display="none";'
        '   gallery.style.display="flex";'
        '   mode="gallery";'
        '   window.scrollTo(0, scrollPos);'
        '   document.title="Gallery";'
        '}'
        'let selected = -1;'
        'let viewerIdx = -1;'
        'let scrollPos = 0;'
        'let mode = "gallery";'
        'const gallery = document.getElementById("gallery");'
        'const imgs = document.getElementsByClassName("img");'
        'const viewer = document.getElementById("viewer");'
        'const viewerImg = document.getElementById("viewerImg");'
        'const left = document.getElementById("left");'
        'const right = document.getElementById("right");'
        'Array.from(imgs).forEach((img, idx) => {'
        '   img.addEventListener("click", (event) => {'
        '       if (selected != -1) {'
        '           imgs[selected].classList.remove("selected");'
        '           selected = -1;'
        '       }'
        '       viewImg(idx);'
        '   }, false);'
        '});'
        'document.addEventListener("keydown", (event) => {'
        '   switch (event.key) {'
        '       case "ArrowLeft":'
        '           switch (mode) {'
        '               case "gallery":'
        '                   selectLeft();'
        '                   break;'
        '               case "viewer":'
        '                   goLeft();'
        '                   break;'
        '           }'
        '           break;'
        '       case "ArrowRight":'
        '           switch (mode) {'
        '               case "gallery":'
        '                   selectRight();'
        '                   break;'
        '               case "viewer":'
        '                   goRight();'
        '                   break;'
        '           }'
        '           break;'
        '       case "ArrowUp":'
        '           if (mode === "gallery") {'
        '               event.preventDefault();'
        '               selectUp();'
        '           }'
        '           break;'
        '       case "ArrowDown":'
        '           if (mode === "gallery") {'
        '               event.preventDefault();'
        '               selectDown();'
        '           }'
        '           break;'
        '       case "+":'
        '           if (mode === "viewer")'
        '               zoomIn();'
        '           break;'
        '       case "-":'
        '           if (mode === "viewer")'
        '               zoomOut();'
        '           break;'
        '       case "0":'
        '           if (mode === "viewer")'
        '               zoomFit();'
        '           break;'
        '       case ".":'
        '           if (mode === "viewer")'
        '               zoomFull();'
        '           break;'
        '       case "Enter":'
        '           if (mode === "gallery" && selected !== -1)'
        '               viewImg(selected);'
        '           break;'
        '       case "Escape":'
        '           if (mode === "viewer")'
        '               showGallery();'
        '           break;'
        '       case "q":'
        '           window.close();'
        '           break;'
        '   }'
        '}, false);'
        'document.addEventListener("wheel", (event) => {'
        '   if (mode === "viewer") {'
        '       event.preventDefault();'
        '       if (event.deltaY < 0)'
        '           zoomIn();'
        '       else if (event.deltaY > 0)'
        '           zoomOut();'
        '   }'
        '}, { "passive": false, "capture": false });'
        'document.addEventListener("auxclick", (event) => {'
        '   if (event.button === 1 && mode === "viewer") {'
        '       if (event.detail == 1)'
        '           zoomFit();'
        '       else'
        '           zoomFull();'
        '   }'
        '}, false);'
        'document.addEventListener("contextmenu", (event) => {'
        '   if (mode === "viewer") {'
        '       event.preventDefault();'
        '       showGallery();'
        '   }'
        "}, false);"
        'document.addEventListener("mousemove", (event) => {'
        '   if (mode === "viewer" && event.buttons === 1)'
        '       window.scrollBy(-event.movementX, -event.movementY);'
        '}, false);'
        'left.addEventListener("click", (event) => {'
        '   if (mode === "viewer")'
        '       goLeft();'
        '}, false);'
        'right.addEventListener("click", (event) => {'
        '   if (mode === "viewer")'
        '       goRight();'
        '}, false);'
        '</script>'
    )

    # End HTML.
    html += (
        '</body>'
        '</html>'
    )

    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf8') as file_obj:
        file_obj.write(html)


def create_gallery(
    dir_path: str,
    randomize: bool = False,
    height: int = 300,
    padding: int = 5,
    no_resize: bool = False,
    as_server: bool = False,


) -> Union[str, None]:
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
    no_resize : bool, optional
        Do not resize images for thumbnails if True. (default=False)
    as_server : bool, optional
        Run a http server instead of opening the HTML file directly. (default=False)

    Returns
    -------
    str | None
        Path to gallery HTML or None if there were no images in directory.
    """
    # Create directories to store the html files.
    if SYSTEM == 'Windows':
        out_dir = os.path.join(os.environ['LOCALAPPDATA'], 'gallery.py')  # Use AppData\Local in Windows.
    elif SYSTEM == 'Linux':
        out_dir = os.path.join(os.environ['HOME'], '.local', 'share', 'gallery.py')  # Use .local/share in Linux.
    os.makedirs(out_dir, exist_ok=True)

    # Clean older files from directory.
    old_files = os.listdir(out_dir)
    for file in old_files:
        os.remove(os.path.join(out_dir, file))

    # Get all images.
    img_files, img_infos = get_img_files(dir_path)

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

    if not no_resize:
        # Resize the images for thumbnails.
        resize_imgs(img_files, img_ids, out_dir, height)

    # Write out HTML file.
    write_html(img_files, img_ids, img_infos, out_dir, height, padding, no_resize, as_server)

    return os.path.join(out_dir, 'index.html')


def open_gallery(html_path: str, browser: List[str] = BROWSER, as_server: bool = False) -> None:
    """Given a path open it in the browser.

    Parameters
    ----------
    html_path : str
        Path to HTML file.
    browser : List[str]
        Command line for browser.
    as_server : bool, optional
        Run a http server instead of opening the HTML file directly. (default=False)
    """
    if as_server:
        subprocess.Popen(browser + ['http://127.0.0.1:8000/index.html'])
        os.chdir(os.path.dirname(html_path))

        # Initialize server and setup socket reuse.
        httpd = socketserver.TCPServer(('', 8000), HTTPRequestHandler, bind_and_activate=False)
        httpd.allow_reuse_address = True

        # Bind server.
        try:
            httpd.server_bind()
            httpd.server_activate()
            print('Serving at port 8000...')
        except:
            httpd.server_close()
            raise

        # Start serving.
        try:
            httpd.serve_forever()
        except:
            print('Shutting down server.')
            httpd.shutdown()
            httpd.server_close()
            raise
    else:
        subprocess.run(browser + [html_path])


def main() -> None:
    """Main function for the script"""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_path', help='Directory containing the images')
    parser.add_argument('-r', '--randomize', help='Randomize the order of the images', action='store_true')
    parser.add_argument('-t', '--height', help='Height of each row in pixels', type=int, default=300)
    parser.add_argument('-p', '--padding', help='Padding between images', type=int, default=5)
    parser.add_argument('-n', '--no_resize', help='Do not resize images for thumnails.', action='store_true')
    parser.add_argument('-s', '--as_server', help='Run a http server', action='store_true')
    parser.add_argument('-b', '--browser', help='Custom browser command (arguments supported)',
                        nargs=argparse.REMAINDER)
    args = parser.parse_args()

    # Use normalized absolute path internally.
    args.dir_path = os.path.normpath(os.path.abspath(args.dir_path))

    # If browser command is not provided use default.
    if args.browser is None:
        args.browser = BROWSER

    # Create gallery and then open it.
    html_path = create_gallery(args.dir_path, args.randomize, args.height, args.padding, args.no_resize, args.as_server)
    if html_path:
        open_gallery(html_path, args.browser, args.as_server)
    else:
        print('No images were found in the directory.')


if __name__ == '__main__':
    main()
