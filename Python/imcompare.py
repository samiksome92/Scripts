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

import cv2
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


def filesize(size):
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


def getpairs(dir_paths, cross=False, max_aspect=0.1):
    """Given a set of directories gathers image pairs for comparison.

    Parameters
    ----------
    dir_paths : list[str]
        Image directories.
    cross : bool, optional
        If True compares across directories. (default=False)
    max_aspect : float, optional
        Maximum aspect ratio difference between image pairs. (default=0.1)

    Returns
    -------
    img_pairs : list[tuple]
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


def similarity(img_1, img_2, resolution=100):
    """Given two images measures their similarity using ssim.

    Parameters
    ----------
    img_1 : dict
        First image.
    img_2 : dict
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

    # Read images, convert to grayscale and resize.
    im_1 = cv2.imread(img_1['path'])
    im_2 = cv2.imread(img_2['path'])
    im_1 = cv2.cvtColor(im_1, cv2.COLOR_BGR2GRAY)
    im_2 = cv2.cvtColor(im_2, cv2.COLOR_BGR2GRAY)
    im_1 = cv2.resize(im_1, (width, height))
    im_2 = cv2.resize(im_2, (width, height))

    # Calcluate SSIM score.
    score = structural_similarity(im_1, im_2)

    return score


def start(img_pairs):
    """Starts the Qt GUI application for user to select images.

    Parameters
    ----------
    img_pairs : list[tuple]
        Image pairs for comparison.

    Returns
    -------
    discarded : list[str]
        List of discarded images. Only the paths are returned.
    """
    # Set up Qt app.
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    discarded = set()

    class BackEnd(QObject):
        """Class for handling image update operations."""

        def __init__(self):
            """Constructor. Sets up first image pair."""
            QObject.__init__(self)
            self.pair_idx = 0
            self.img_left = img_pairs[self.pair_idx]['img_pair'][0]
            self.img_right = img_pairs[self.pair_idx]['img_pair'][1]
            self.score = img_pairs[self.pair_idx]['score']
            self.update()

        def update(self):
            """Updates the image pair and associated status text."""
            format_left = self.img_left['format']
            width_left = self.img_left['width']
            height_left = self.img_left['height']
            size_left = self.img_left['size']

            format_right = self.img_right['format']
            width_right = self.img_right['width']
            height_right = self.img_right['height']
            size_right = self.img_right['size']

            txt_left = ''
            txt_right = ''

            # Consider PNG better than JPEG.
            if format_left == format_right:
                txt_left += f'{format_left}<br>'
                txt_right += f'{format_right}<br>'
            elif format_left == 'PNG' and format_right == 'JPEG':
                txt_left += f'<font color="{COLOR_BETTER}">PNG</font><br>'
                txt_right += f'<font color="{COLOR_WORSE}">JPEG</font><br>'
            elif format_left == 'JPEG' and format_right == 'PNG':
                txt_left += f'<font color="{COLOR_WORSE}">JPEG</font><br>'
                txt_right += f'<font color="{COLOR_BETTER}">PNG</font><br>'
            else:
                txt_left += f'<font color="{COLOR_DIFF}">{format_left}</font><br>'
                txt_right += f'<font color="{COLOR_DIFF}">{format_right}</font><br>'

            # If both width and height of one image is larger than the other consider it better.
            if width_left == width_right and height_left == height_right:
                txt_left += f'{width_left} x {height_left}<br>'
                txt_right += f'{width_right} x {height_right}<br>'
            elif width_left > width_right and height_left > height_right:
                txt_left += f'<font color="{COLOR_BETTER}">{width_left} x {height_left}</font><br>'
                txt_right += f'<font color="{COLOR_WORSE}">{width_right} x {height_right}</font><br>'
            elif width_left < width_right and height_left < height_right:
                txt_left += f'<font color="{COLOR_WORSE}">{width_left} x {height_left}</font><br>'
                txt_right += f'<font color="{COLOR_BETTER}">{width_right} x {height_right}</font><br>'
            else:
                txt_left += f'<font color="{COLOR_DIFF}">{width_left} x {height_left}<br>'
                txt_right += f'<font color="{COLOR_DIFF}">{width_right} x {height_right}<br>'

            # Larger size is better.
            if size_left == size_right:
                txt_left += f'{filesize(size_left)}<br>'
                txt_right += f'{filesize(size_right)}<br>'
            elif size_left > size_right:
                txt_left += f'<font color="{COLOR_BETTER}">{filesize(size_left)}</font><br>'
                txt_right += f'<font color="{COLOR_WORSE}">{filesize(size_right)}</font><br>'
            elif size_left < size_right:
                txt_left += f'<font color="{COLOR_WORSE}">{filesize(size_left)}</font><br>'
                txt_right += f'<font color="{COLOR_BETTER}">{filesize(size_right)}</font><br>'
            else:
                txt_left += f'<font color="{COLOR_DIFF}">{filesize(size_left)}</font><br>'
                txt_right += f'<font color="{COLOR_DIFF}">{filesize(size_right)}</font><br>'

            txt_score = f'{self.score*100:.2f}%'

            # Update images and text.
            view.rootContext().setContextProperty('img_left', QUrl.fromLocalFile(self.img_left['path']))
            view.rootContext().setContextProperty('img_right', QUrl.fromLocalFile(self.img_right['path']))
            view.rootContext().setContextProperty('txt_left', txt_left)
            view.rootContext().setContextProperty('txt_right', txt_right)
            view.rootContext().setContextProperty('txt_score', txt_score)

        @Slot(str)
        def next(self, chosen):
            """Load the next image pair.

            Parameters
            ----------
            chosen : str
                Which image was chosen for the last pair
            """
            if chosen == 'left':
                discarded.add(self.img_right['path'])
            elif chosen == 'right':
                discarded.add(self.img_left['path'])

            self.pair_idx += 1

            if self.pair_idx == len(img_pairs):
                QGuiApplication.quit()
            else:
                self.img_left = img_pairs[self.pair_idx]['img_pair'][0]
                self.img_right = img_pairs[self.pair_idx]['img_pair'][1]
                self.score = img_pairs[self.pair_idx]['score']

                # If one of the images has already been discarded skip the pair.
                if self.img_left['path'] in discarded or self.img_right['path'] in discarded:
                    self.next('both')

                self.update()

    # Register BackEnd class and load QML.
    backend = BackEnd()
    view.rootContext().setContextProperty('backend', backend)
    view.setSource(QUrl.fromLocalFile(os.path.join(os.path.split(__file__)[0], 'Resources/imcompare_view.qml')))
    view.showMaximized()

    app.exec()

    return discarded


def main():
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
    args = parser.parse_args()

    # Cross comparison cannot be done without two directories.
    if args.cross and len(args.dirs) < 2:
        print('Cross comparison requires at least two directories.')
        exit()

    # Get image pairs.
    img_pairs = getpairs(args.dirs, args.cross, args.max_aspect)

    # Calculate similarities.
    scores = []
    progress_bar = tqdm(img_pairs, bar_format='Comparing images |{bar:20}| {n_fmt}/{total_fmt}')
    for img1, img2 in progress_bar:
        score = similarity(img1, img2, args.resolution)
        scores.append(score)

    # Sort pairs in descending order of similarity score.
    img_pairs = [{'score': scores[i], 'img_pair': p} for i, p in enumerate(img_pairs)]
    img_pairs = sorted(img_pairs, key=lambda x: x['score'], reverse=True)

    # Start Qt GUI for user to select images.
    discarded = start(img_pairs)

    # Append .discarded to discarded image files.
    for img_path in discarded:
        os.rename(img_path, img_path+'.discarded')
    print(f'{len(discarded)} images discarded.')


if __name__ == '__main__':
    main()
