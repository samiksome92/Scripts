#!/usr/bin/env python3

"""Takes a list of directories as input and allows comparing images in them for possible duplicates.

Given a list of directories, the script scans them for images. Next it compares similarities between pairs of images
using SSIM algorithm. Once the similarities have been computed a Qt GUI is started so that users can manually look at
pairs of images and select which ones to keep. The discarded images are renamed with a .discarded extension.
"""

import argparse
import itertools
import os
import sys
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
from PIL import Image
from PySide6.QtCore import Slot, QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from skimage.metrics import structural_similarity
from tqdm import tqdm

SUPPORTED_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']
COLOR_BETTER = '#2e7d32'
COLOR_WORSE = '#c62828'
COLOR_DIFF = '#f9a825'


def filesize(size: int) -> str:
    """Given file size in bytes returns human readable string.

    Parameters
    ----------
    size : int
        Size in bytes.

    Returns
    -------
    str
        Human readable string of the given size.
    """
    # Keep dividing until quotient is zero.
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    unit_idx = 0
    while size // 1024 > 0:
        size = size / 1024
        unit_idx += 1

        # If last unit has been reached break out.
        if unit_idx == len(units) - 1:
            break

    return f'{size:.2f} {units[unit_idx]}'


def getpairs(dir_paths: List[str], cross: bool = False, max_aspect: float = 0.1) -> List[Tuple]:
    """Given a set of directories gathers image pairs for comparison.

    Parameters
    ----------
    dir_paths : List[str]
        Image directories.
    cross : bool, optional
        If True compares across directories. (default=False)
    max_aspect : float, optional
        Maximum aspect ratio difference between image pairs. (default=0.1)

    Returns
    -------
    img_pairs : List[Tuple]
        Pairs of images for comparison.
    """
    # Gather all valid images.
    imgs = {}
    dir_paths = sorted(dir_paths)
    for dir_path in dir_paths:
        imgs[dir_path] = []
        file_list = sorted([os.path.join(dir_path, f) for f in os.listdir(dir_path)])
        progress_bar = tqdm(file_list, bar_format='Checking all files |{bar:20}| {n_fmt}/{total_fmt}')
        for file_path in progress_bar:
            try:
                with Image.open(file_path, 'r') as im:
                    if im.format in SUPPORTED_FORMATS:
                        imgs[dir_path].append({
                            'path': file_path,
                            'format': im.format,
                            'width': im.size[0],
                            'height': im.size[1],
                            'size': os.stat(file_path).st_size
                        })
            except IOError:
                pass

    # If cross is specified only consider pairs across directories, not within them.
    if cross:
        img_pairs = []
        for dir_path_1, dir_path_2 in itertools.combinations(dir_paths, 2):
            imgs_1 = imgs[dir_path_1]
            imgs_2 = imgs[dir_path_2]
            for img_1 in imgs_1:
                aspect_1 = img_1['width']/img_1['height']
                for img_2 in imgs_2:
                    aspect_2 = img_2['width']/img_2['height']

                    # Skip pair if aspect ratio difference is larger than max_aspect.
                    if abs(aspect_1 - aspect_2) > max_aspect:
                        continue

                    img_pairs.append((img_1, img_2))
    else:
        img_pairs = []
        imgs_list = [img for dir_path in dir_paths for img in imgs[dir_path]]
        for img_1, img_2 in itertools.combinations(imgs_list, 2):
            aspect_1 = img_1['width']/img_1['height']
            aspect_2 = img_2['width']/img_2['height']

            # Skip pair if aspect ratio difference is larger than max_aspect.
            if abs(aspect_1 - aspect_2) > max_aspect:
                continue

            img_pairs.append((img_1, img_2))

    return img_pairs


def similarity(img_1: Dict, img_2: Dict, resolution: int = 100) -> float:
    """Given two images measures their similarity using ssim.

    Parameters
    ----------
    img_1 : Dict
        First image.
    img_2 : Dict
        Second image.
    resolution : int, optional
        Images are resized to this resolution before comparison. (default=100)

    Returns
    -------
    score : float
        SSIM score.
    """
    # Get average aspect ratio.
    aspect_1 = img_1['width']/img_1['height']
    aspect_2 = img_2['width']/img_2['height']
    avg_aspect = (aspect_1 + aspect_2) / 2

    # Calculate resized width and height
    if avg_aspect < 1:
        width = int(resolution * avg_aspect)
        height = int(resolution)
    else:
        width = int(resolution)
        height = int(resolution / avg_aspect)

    # Read images (via numpy to support unicode paths), convert to grayscale and resize.
    im_1 = np.fromfile(img_1['path'], dtype='uint8')
    im_2 = np.fromfile(img_2['path'], dtype='uint8')
    im_1 = cv2.imdecode(im_1, cv2.IMREAD_GRAYSCALE)
    im_2 = cv2.imdecode(im_2, cv2.IMREAD_GRAYSCALE)
    im_1 = cv2.resize(im_1, (width, height))
    im_2 = cv2.resize(im_2, (width, height))

    # Calcluate SSIM score.
    score = structural_similarity(im_1, im_2)

    return score


def start(img_pairs: List[Tuple], return_selected: bool = False) -> Union[List[str], Tuple[List[str], List[str]]]:
    """Starts the Qt GUI application for user to select images.

    Parameters
    ----------
    img_pairs : List[tuple]
        Image pairs for comparison.
    return_selected : bool, optional
        If True return selected images as well as discarded ones. (default=False)

    Returns
    -------
    discarded : List[str]
        List of discarded images. Only the paths are returned.
    selected : List[str]
        List of selected images. Only returned if return_selected=True.
    """
    # Set up Qt app.
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    discarded = set()
    selected = set()

    class BackEnd(QObject):
        """Class for handling image update operations."""

        def __init__(self):
            """Constructor. Sets up first image pair."""
            QObject.__init__(self)
            self.pair_idx = 0
            self.which = "left"
            self.img_left = img_pairs[self.pair_idx]['img_pair'][0]
            self.img_right = img_pairs[self.pair_idx]['img_pair'][1]
            self.txt_left = ''
            self.txt_right = ''
            self.score = img_pairs[self.pair_idx]['score']
            self.maketext()
            self.update()

        def maketext(self):
            """Creates formatted status text."""
            format_left = self.img_left['format']
            width_left = self.img_left['width']
            height_left = self.img_left['height']
            size_left = self.img_left['size']

            format_right = self.img_right['format']
            width_right = self.img_right['width']
            height_right = self.img_right['height']
            size_right = self.img_right['size']

            self.txt_left = f'{self.score*100:.2f}%&nbsp;&nbsp;&nbsp;&nbsp;'
            self.txt_right = f'{self.score*100:.2f}%&nbsp;&nbsp;&nbsp;&nbsp;'

            # Consider PNG better than JPEG.
            if format_left == format_right:
                self.txt_left += f'{format_left}&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'{format_right}&nbsp;&nbsp;&nbsp;&nbsp;'
            elif format_left == 'PNG' and format_right == 'JPEG':
                self.txt_left += f'<font color="{COLOR_BETTER}">PNG</font>&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'<font color="{COLOR_WORSE}">JPEG</font>&nbsp;&nbsp;&nbsp;&nbsp;'
            elif format_left == 'JPEG' and format_right == 'PNG':
                self.txt_left += f'<font color="{COLOR_WORSE}">JPEG</font>&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'<font color="{COLOR_BETTER}">PNG</font>&nbsp;&nbsp;&nbsp;&nbsp;'
            else:
                self.txt_left += f'<font color="{COLOR_DIFF}">{format_left}</font>&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'<font color="{COLOR_DIFF}">{format_right}</font>&nbsp;&nbsp;&nbsp;&nbsp;'

            # If both width and height of one image is larger than the other consider it better.
            if width_left == width_right and height_left == height_right:
                self.txt_left += f'{width_left} x {height_left}&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'{width_right} x {height_right}&nbsp;&nbsp;&nbsp;&nbsp;'
            elif width_left > width_right and height_left > height_right:
                self.txt_left += f'<font color="{COLOR_BETTER}">{width_left} x {height_left}</font>&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'<font color="{COLOR_WORSE}">{width_right} x {height_right}</font>&nbsp;&nbsp;&nbsp;&nbsp;'
            elif width_left < width_right and height_left < height_right:
                self.txt_left += f'<font color="{COLOR_WORSE}">{width_left} x {height_left}</font>&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'<font color="{COLOR_BETTER}">{width_right} x {height_right}</font>&nbsp;&nbsp;&nbsp;&nbsp;'
            else:
                self.txt_left += f'<font color="{COLOR_DIFF}">{width_left} x {height_left}&nbsp;&nbsp;&nbsp;&nbsp;'
                self.txt_right += f'<font color="{COLOR_DIFF}">{width_right} x {height_right}&nbsp;&nbsp;&nbsp;&nbsp;'

            # Larger size is better.
            if size_left == size_right:
                self.txt_left += f'{filesize(size_left)}'
                self.txt_right += f'{filesize(size_right)}'
            elif size_left > size_right:
                self.txt_left += f'<font color="{COLOR_BETTER}">{filesize(size_left)}</font>'
                self.txt_right += f'<font color="{COLOR_WORSE}">{filesize(size_right)}</font>'
            elif size_left < size_right:
                self.txt_left += f'<font color="{COLOR_WORSE}">{filesize(size_left)}</font>'
                self.txt_right += f'<font color="{COLOR_BETTER}">{filesize(size_right)}</font>'
            else:
                self.txt_left += f'<font color="{COLOR_DIFF}">{filesize(size_left)}</font>'
                self.txt_right += f'<font color="{COLOR_DIFF}">{filesize(size_right)}</font>'

        def update(self):
            """Updates image and status text."""
            if self.which == "left":
                view.rootContext().setContextProperty('img', QUrl.fromLocalFile(self.img_left['path']))
                view.rootContext().setContextProperty('txt', self.txt_left)
            elif self.which == "right":
                view.rootContext().setContextProperty('img', QUrl.fromLocalFile(self.img_right['path']))
                view.rootContext().setContextProperty('txt', self.txt_right)

        @Slot()
        def switch(self):
            """Load the next image pair."""
            if self.which == 'left':
                self.which = 'right'
            elif self.which == 'right':
                self.which = 'left'

            self.update()

        @Slot()
        def next(self):
            """Load the next image pair."""
            self.pair_idx += 1

            if self.pair_idx == len(img_pairs):
                QGuiApplication.quit()
            else:
                self.img_left = img_pairs[self.pair_idx]['img_pair'][0]
                self.img_right = img_pairs[self.pair_idx]['img_pair'][1]
                self.score = img_pairs[self.pair_idx]['score']

                # If one of the images has already been discarded skip the pair.
                if self.img_left['path'] in discarded or self.img_right['path'] in discarded:
                    self.next()

                self.which = "left"
                self.maketext()
                self.update()

        @Slot()
        def choose(self):
            """Choose one of the images and load the next image pair."""
            if self.which == 'left':
                discarded.add(self.img_right['path'])
                selected.add(self.img_left['path'])
            elif self.which == 'right':
                discarded.add(self.img_left['path'])
                selected.add(self.img_right['path'])

            self.next()

        @Slot()
        def both(self):
            """Choose both images and load the next image pair."""
            selected.add(self.img_left['path'])
            selected.add(self.img_right['path'])

            self.next()

    # Register BackEnd class and load QML.
    backend = BackEnd()
    view.rootContext().setContextProperty('backend', backend)
    view.setSource(QUrl.fromLocalFile(os.path.join(os.path.split(__file__)[0], 'Resources/imcompare_view.qml')))
    view.showMaximized()

    app.exec()

    # Make sure no discarded files are present in selected.
    selected = [f for f in selected if f not in discarded]
    if return_selected:
        return list(discarded), selected
    else:
        return list(discarded)


def main() -> None:
    """Main method for the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', help='Image directories', nargs='+')
    parser.add_argument('-x', '--cross', help='Compare across directories, not within them', action='store_true')
    parser.add_argument('-r', '--resolution', help='Resolution at which the SSIM is computed', type=int, default=100)
    parser.add_argument(
        '-a',
        '--max_aspect',
        help='If difference between aspect ratios are higher than this, images are not considered for comparison',
        type=float,
        default=0.1
    )
    parser.add_argument('-m', '--mark_selected',
                        help='Mark selected ones as well as discarded ones', action='store_true')
    args = parser.parse_args()

    # Cross comparison cannot be done without two directories.
    if args.cross and len(args.dirs) < 2:
        print('Cross comparison requires at least two directories.')
        exit()

    # Get image pairs.
    img_pairs = getpairs(args.dirs, args.cross, args.max_aspect)

    # Calculate similarities.
    scores = []
    progress_bar = tqdm(img_pairs, bar_format='Comparing images   |{bar:20}| {n_fmt}/{total_fmt}')
    for img1, img2 in progress_bar:
        score = similarity(img1, img2, args.resolution)
        scores.append(score)

    # Sort pairs in descending order of similarity score.
    img_pairs = [{'score': scores[i], 'img_pair': p} for i, p in enumerate(img_pairs)]
    img_pairs = sorted(img_pairs, key=lambda x: x['score'], reverse=True)

    # Start Qt GUI for user to select images.
    discarded, selected = start(img_pairs, True)

    # Append .discarded to discarded image files.
    for img_path in discarded:
        os.rename(img_path, img_path+'.discarded')
    print(f'{len(discarded)} images discarded.')

    # If mark_selected is mentioned, append .selected to selected image files.
    if args.mark_selected:
        for img_path in selected:
            os.rename(img_path, img_path+'.selected')
        print(f'{len(selected)} images selected.')


if __name__ == '__main__':
    main()
