# A Collection of Small Scripts

This is simply a collection of scripts to make my life easier.

## AutoHotkey Scripts
- [`AutoClick.ahk`](#AutoClickahk)

## JavaScript Scripts
- [`desktopWikipedia.js`](#desktopWikipediajs)
- [`nyaaMagnet.js`](#nyaaMagnetjs)
- [`oldReddit.js`](#oldRedditjs)
- [`twitterImage.js`](#twitterImagejs)

## Python Scripts
- [`crop.py`](#croppy)
- [`gallery.py`](#gallerypy)
- [`gif2mkv.py`](#gif2mkvpy)
- [`imcompare.py`](#imcomparepy)
- [`makecbz.py`](#makecbzpy)

## `AutoClick.ahk`
A simple script to automatically click repeatedly via a toggle switch. The time in between clicks can be changed by setting the SLEEP_TIME variable to appropriate value in milliseconds.

---

## `crop.py`
A script to crop an image in an intelligent manner trying to keep the most important parts.

Given an image the script currently maximises the crop location w.r.t. image gradients. If requested the image is first resized to fit one crop dimension.

### Requirements
- `opencv-python`
- `numpy`
- `pillow`

### Usage
    crop.py [-h] [-f] [-o OUT_FILE] img_path crop_size

positional arguments:

    img_path              Image to crop
    crop_size             Crop size as WxH

optional arguments:

    -h, --help            show this help message and exit
    -f, --fit             Resize image to fit one crop dimension
    -o OUT_FILE, --out_file OUT_FILE
                            Output file

Supply the image path, the crop size and optionally the fit parameter and output file. The crop size must be specified as `WxH` (e.g. `500x500`). If the crop size is bigger than the image, an error is printed and the script terminates. The `--fit` parameter if specified resizes the image (while maintaining the aspect ratio) to fit one of the crop dimensions. If the output file is not specified the output is placed in the same directory as the image with the name `<image>_cropped.png`

A good and a bad example.

Image | Crop without fit | Crop with fit
--- | --- | ---
![](examples/crop_1.jpg) | ![](examples/crop_1_out.png) | ![](examples/crop_1_out_fit.png)
![](examples/crop_2.jpg) | ![](examples/crop_2_out.png) | ![](examples/crop_2_out_fit.png)

(Images courtesy of [Unsplash](https://unsplash.com/))

It works well if the actual region of interest has the most edges, otherwise it fails since it only really looks at the density of edges in the image to decide the most important region

---

## `desktopWikipedia.js`
A simple user script to redirect mobile english wikipedia links to their desktop versions. The script replaces `*.m.wikipedia.org` with `*.wikipedia.org` in url to achieve this.

---

## `gallery.py`
This script takes a directory as input and shows all images inside it as a gallery.

The script scans a given directory for supported image files. It then generates HTML pages for a gallery populated with found images. Once the HTML files have been created, the gallery is shown using the default web browser. Supports keyboard and mouse navigation.

### Requirements
- `pillow`
- `tqdm`

### Usage
    gallery.py [-h] [-r] [-t HEIGHT] [-p PADDING] [-b ...] dir_path

positional arguments

    dir_path              Directory containing the images

optional arguments:

    -h, --help            show this help message and exit
    -r, --randomize       Randomize the order of the images
    -t HEIGHT, --height HEIGHT
                          Height of each row in pixels
    -p PADDING, --padding PADDING
                          Padding between images
    -b ..., --browser ...
                          Custom browser command (arguments supported)

The gallery is laid out as shown in this example.
![](examples/gallery.png)
(Images courtesy of [Unsplash](https://unsplash.com/))

The images can be clicked to go into single view mode, where only that image is shown. Standard `left`/`right` keyboard navigation is supported, as is `+`, `-`, `0` for zooming.

By default padding of 5px is used but can be overridden using `--padding` parameter. Similarly the default height of each row is 300px and can be overridden by specifying `--height`.

If `--randomize` is specified, the order of the images will be randomized (it will still try to keep multipart images, such as `img1`, `img2`, etc., together). Without `--randomize` the images are laid out in alphabetical order.

Finally, a custom browser can be used via the parameter `--browser`. Arguments to said browser command can also be provided.

<b>NOTE</b>: `--browser` should be specified at the very end since any argument following it is considered part of the browser command.

---

## `gif2mkv.py`
A simple script that converts gif to mkv.

This script takes a animated gif image and converts it to H.265 video in mkv container using imagemagick, ffmpeg and mkvmerge. The last frame is duplicated to make sure last frame delay is not dropped.

### Requirements
- `ffmpeg`
- `mkvmerge`
- `pillow`

### Usage
    gif2mkv.py [-h] [--out_file OUT_FILE] [--bg_color BG_COLOR] gif_file

positional arguments:

    gif_file             gif file to convert

optional arguments:

    -h, --help            show this help message and exit
    --out_file OUT_FILE   output file
    --bg_color BG_COLOR  the background color as a hex code eg. #2f213d

Directly converting from gif to H.265 encoded mkv using ffmpeg causes certain issues such as dropping the last frame delay. This script tries to rectify that.

The script extracts frames from gif using imagemagick and composes them onto a solid background color. It then checks whether the gif has a constant or variable fps and proceeds accordingly. For constant fps the encoding is straight forward and uses only `ffmpeg`. However, for variable fps `ffmpeg`'s `concat` demuxer does not always produce proper timings (based on our experiments). As such, we first encode using `ffmpeg` at a constant fps followed by setting timecodes explicitly using `mkvmerge`. The last frame is also duplicated in both cases so that it is shown properly.

---

## `imcompare.py`
Takes a list of directories as input and allows comparing images in them for possible duplicates.

Given a list of directories, the script scans them for images. Next it compares similarities between pairs of images using SSIM algorithm. Once the similarities have been computed a Qt GUI is started so that users can manually look at pairs of images and select which ones to keep. The discarded images are renamed with a .discarded extension.

### Requirements
- `opencv-python`
- `pillow`
- `pyside6`
- `scikit-image`
- `tqdm`

### Usage
    usage: imcompare.py [-h] [-x] [-r RESOLUTION] [-a MAX_ASPECT] dirs [dirs ...]

positional arguments:

    dirs                  Image directories

optional arguments:

    -h, --help            show this help message and exit
    -x, --cross           Compare across directories, not within them
    -r RESOLUTION, --resolution RESOLUTION
                          Resolution at which the SSIM is computed
    -a MAX_ASPECT, --max_aspect MAX_ASPECT
                          If difference between aspect ratios are higher than this, images are not considered for
                          comparison

Supply a list of directories with images to compare them visually, primarily used for filtering out same images saved with varying quality and formats.

By default the images found in all directories are considered together and all possible pairs are looked at. If `--cross` is specified images in the same directory are not compared with each other. As such `--cross` needs at least two directories to work.

The similarities between images are calculate using structured similarity index (SSIM). Since evaluating SSIM over high resolution images is very costly, images are resized to fit a box whose size can be specified using `--resolution`. By default it is 100 x 100. To prune out further unlikely pairs if the difference in aspect ratio of two images is larger than `--max_aspect` they are not considered (default value is 0.1).

Once similarities have been computed a GUI is started which shows image pairs in descending order of similarity so that the user can choose which ones to keep. Clicking on an image keeps it and discards the other. Clicking on the information area keeps both images. The process can be stopped any time by simply closing the window.

The discarded images are then renamed in place and `.discarded` is appended to their file names making it their extension.

**NOTE**: Requires `Resources/imcompare_view.qml` file to be present.

---

## `makecbz.py`
This script takes a directory as input and produces a CBZ file as output.

Given a directory with images, it first checks all images for supported formats and possible corrupted images. Once checked all images are converted to JPEG format with specified quality factor, if they are larger than specified resolution they are scaled down as well. The images are optionally renamed and packed into a zip file.

### Requirements
- `pillow`
- `tqdm`

### Usage
    makecbz.py [-h] [-r RESOLUTION] [-j] [-p] [-q QUALITY] [-n] [-d] dir_paths [dir_paths ...]

positional arguments:

    dir_paths             Directory/directories containing the images

optional arguments:

    -h, --help            show this help message and exit
    -r RESOLUTION, --resolution RESOLUTION
                          Maximum horizontal resolution
    -j, --jpeg            Convert all image files to JPEG
    -p, --png             Convert all image files to PNG
    -q QUALITY, --quality QUALITY
                          Quality parameter for JPEG (0-100) or compression level for PNG (0-9)
    -m, --merge_dirs      Merge images in subfolders
    -n, --no_rename       Don't rename files
    -d, --delete          Delete original files

Supply a directory or a list of directories (of images) to convert them into CBZ files. If there are non-image files, non-supported formats or corrupted images then a list of such files is printed out.

The images are scaled according to their aspect ratios and the specified `--resolution`. The standard aspect ratio is considered to be 2/3. Images with smaller aspect ratios (taller) are scaled to some multiple of `--resolution` in steps of `0.25 * --resolution`. If no resolution is specified the images are not scaled.

If `--jpeg` is speicified all images are converted to JPEG. Similarly if `--png` is specified all images are converted to PNG. If none is specified images are kept in their source format.

`--quality` specifies the JPEG compression quality or PNG compression level for `pillow`. It must be an integer between 0 and 100 for JPEG and 0-9 for PNG.

If `--merge_dirs` is specified images in sub-directories are moved to the parent directory while appending the sub-directory's name before it. Useful if the comic contains logical parts which should have a common prefix (Should generally be used along with `--no-rename` to keep said prefixes).

`--no-rename` if specified keeps the original file names of the images, otherwise they are renamed as `01.jpg`, `02.jpg`, `03.jpg`, ... (the numbers are padded with as many zeros as required). `--delete` if specified deletes the original image files as well as the directory.

---

## `nyaaMagnet.js`
This script adds an extra button beside the search button in [nyaa.si](https://nyaa.si), which collects the magnet links for all of the torrents listed in the current page/screen and copies them to the clipboard.

Primary use is searching for torrents of a series and grabbing all magnet links (say for all episodes) in one go.

---

## `oldReddit.js`
A simple user script variant of the Old Reddit Redirect extension by Tom Watson ([GitHub](https://github.com/tom-james-watson/old-reddit-redirect)).

This was created so that if one is already using a user script manager extension (Greasemonkey, Tampermonkey, Violentmonkey, etc.), then they don't need another extension simply for old reddit redirection.

---

## `twitterImage.js`
A script to redirect image urls from twitter to show the original image rather than one of the twitter resized versions. Simply replaces the last part of image urls with `=orig`.
