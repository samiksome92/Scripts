# A Collection of Small Scripts

This is simply a collection of scripts to make my life easier.

## AutoHotkey Scripts
- [`AutoClick.ahk`](#AutoClickahk)

## JavaScript Scripts
- [`desktopWikipedia.js`](#desktopWikipediajs)
- [`nyaaMagnet.js`](#nyaaMagnetjs)
- [`twitterImage.js`](#twitterImagejs)

## PowerShell Scripts
- [`Start-Sandbox.ps1`](#Start-Sandboxps1)

## Python Scripts
- [`crop.py`](#croppy)
- [`dup.py`](#duppy)
- [`fortiauth.py`](#fortiauthpy)
- [`gallery.py`](#gallerypy)
- [`gif2mkv.py`](#gif2mkvpy)
- [`makecbz.py`](#makecbzpy)
- [`nocache.http.server.py`](#nocachehttpserverpy)
- [`passgen.py`](#passgenpy)
- [`txtconv.py`](#txtconvpy)

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

## `dup.py`
Check for and remove duplicate files.

Checks for duplicate files in given directories using size comparison, hashing, and byte-by-byte comparison. By default it removes all duplicates it finds and outputs a list of deleted files. It can also be used to simply output the list of duplicates without deleting them.

### Requirements
- `tqdm`

### Usage
    dup [-h] [-r] [-f] [-n] [-o OUTPUT] dirs [dirs ...]

positional arguments:

    dirs                  Directories to search

optional arguments:

    -h, --help            show this help message and exit
    -r, --recursive       Search directories recursively
    -f, --find            Only find duplicates. Don't delete them
    -n, --no_hash         Don't use any hashing
    -o OUTPUT, --output OUTPUT
                          Output file with list of duplicates

If `--find` is not specified the duplicate files will be deleted. `--recursive` will search directories recursively to find files. Specify `--no_hash` to skip hashing and directly compare files. Unless `--output` is specified no output file will be written (The list of files will still be displayed on the terminal).

---

## `fortiauth.py`
A script to automatically login to fortinet firewall captive portal.

Given a username and password this script automatically monitors the network and logs in to the fortinet captive portal when needed. It also send keepalive requests periodically to maintain the login.

### Requirements
- `requests`

### Usage
    fortiauth.py [-h] [-u USERNAME] [-p PASSWORD] [-r RETRY_TIME] [-k KEEPALIVE_TIME]

optional arguments:

    -h, --help            show this help message and exit
    -u USERNAME, --username USERNAME
                        Username
    -p PASSWORD, --password PASSWORD
                          Password
    -r RETRY_TIME, --retry_time RETRY_TIME
                          Seconds to wait before retrying
    -k KEEPALIVE_TIME, --keepalive_time KEEPALIVE_TIME
                          Seconds to wait between keepalives

If username/password is not supplied the script will prompt for them. By default `retry_time` is 30s and `keepalive_time` is 60s.

---

## `gallery.py`
This script takes a directory as input and shows all images inside it as a gallery.

The script scans a given directory for supported image files. It then generate a HTML page for a gallery populated with found images. Once the HTML file has been created, the gallery is shown using the default web browser. Supports keyboard and mouse navigation.

### Requirements
- `pillow`
- `tqdm`

### Usage
    gallery [-h] [-r] [-t HEIGHT] [-p PADDING] [-n] [-o PORT] [-b ...] dir_path

positional arguments

    dir_path              Directory containing the images

optional arguments:

    -h, --help            show this help message and exit
    -r, --randomize       Randomize the order of the images
    -t HEIGHT, --height HEIGHT
                          Height of each row in pixels
    -p PADDING, --padding PADDING
                          Padding between images
    -n, --no_resize       Do not resize images for thumnails.
    -o PORT, --port PORT  Port to use for the server.
    -b ..., --browser ...
                          Custom browser command (arguments supported)

The gallery is laid out as shown in this example.
![](examples/gallery.png)
(Images courtesy of [Unsplash](https://unsplash.com/))

The images can be clicked to go into single view mode, where only that image is shown. Standard `left`/`right` keyboard navigation is supported, as is `+`, `-`, `0` for zooming.

By default padding of 5px is used but can be overridden using `--padding` parameter. Similarly the default height of each row is 300px and can be overridden by specifying `--height`.

If `--randomize` is specified, the order of the images will be randomized (it will still try to keep multipart images, such as `img1`, `img2`, etc., together). Without `--randomize` the images are laid out in alphabetical order.

By default all images are resized for thumbnails. Using `--no_resize` disables this, which means the gallery launches much faster but images may load slowly if they are large.

The server uses 8000 as the default port, but it can be overridden using `--port`. Useful for launching multiple instances.

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

## `makecbz.py`
This script takes a directory as input and produces a CBZ file as output.

Given a directory with images, it first checks all images for supported formats and possible corruption. The images are then renamed (optionally) and packed into a zip/cbz file. If specified the original image files and directory are deleted.

### Requirements
- `pillow`
- `rich`

### Usage
    makecbz.py [-h] [-n] [-d] dirs [dirs ...]

positional arguments:

    dirs             Directory(s) containing the images

optional arguments:

    -h, --help       show this help message and exit
    -n, --no_rename  Don't rename files
    -d, --delete     Delete original files

Supply a directory or a list of directories (of images) to convert them into CBZ files. If there are non-image files, non-supported formats or corrupted images then a list of such files is printed out. Certain file names (hardcoded) are excluded from such a check.

If `--no-rename` is specified the original file names of the images are kept, otherwise they are renamed as `01.jpg`, `02.jpg`, `03.jpg`, ... (the numbers are padded with as many zeros as required, with a minimum of 2 digits). `--delete` if specified deletes the original image files as well as the directory.

---

## `nocache.http.server.py`
A script implementing a simple http server with custom cache control headers. Usage is same as http.server.

---

## `nyaaMagnet.js`
This script adds an extra button beside the search button in [nyaa.si](https://nyaa.si), which collects the magnet links for all of the torrents listed in the current page/screen and copies them to the clipboard.

Primary use is searching for torrents of a series and grabbing all magnet links (say for all episodes) in one go.

---

## `passgen.py`
A simple password generator.

Generates a secure random password of a given length using the secrets library. By default passwords include lowercase letters, uppercase letters and digits, but not symbols. Options are provided to enable or disable any of the afore mentioned sets. Additionally one can also provide a set of custom symbols.

### Requirements
- `pyperclip`

### Usage
    passgen [-h] [-l LENGTH] [-a] [-na] [-A] [-nA] [-1] [-n1] [-@] [-n@] [--valid_symbols VALID_SYMBOLS] [-c]

optional arguments:

    -h, --help            show this help message and exit
    -l LENGTH, --length LENGTH
                          Length of the generated password
    -a, --lowercase       Use lowercase letters
    -na, --no_lowercase   Don't use lowercase letters
    -A, --uppercase       Use uppercase letters
    -nA, --no_uppercase   Don't use uppercase letters
    -1, --digits          Use digits
    -n1, --no_digits      Don't use digits
    -@, --symbols         Use symbols
    -n@, --no_symbols     Don't use symbols
    --valid_symbols VALID_SYMBOLS
                          Provide a string of characters to use as symbols
    -c, --clipboard       Copy generated password to clipboard instead of displaying it

The length of the password can be specified using `--length` (Default is 15 characters). `--lowercase`, `--no_lowercase`, `--uppercase`, `--no_uppercase`, `--digits`, `--no_digits`, `--symbols`, `--no_symbols` control which characters can be used to generate the password. In addition one can provide a custom string of characters via `--valid_symbols` to act as the symbols set. If `--clipboard` is specified the password is copied to clipboard using `pyperclip`, otherwise it is displayed.

---

## `Start-Sandbox.ps1`
Starts a sandbox with provided configuration options.

### Usage
SYNTAX

    Start-Sandbox.ps1 [[-vGPU] <String>] [[-Networking] <String>] [[-MappedFolders] <Hashtable[]>] 
    [[-LogonCommand] <String>] [[-AudioInput] <String>] [[-VideoInput] <String>] [[-ProtectedClient] <String>]
    [[-PrinterRedirection] <String>] [[-ClipboardRedirection] <String>] [[-MemoryInMB] <Int32>] [<CommonParameters>]

PARAMETERS

    -vGPU <String>
        Enable or disable vGPU. If not provided default is used.

    -Networking <String>
        Disable networking. If not provided default is used.

    -MappedFolders <Hashtable[]>
        Array of folders to map in the sandbox. Input should be an array of hashmaps with keys HostFolder,
        SandboxFolder and ReadOnly.

    -LogonCommand <String>
        Command to execute upon logging on.

    -AudioInput <String>
        Enable or disable audio input. If not provided default is used.

    -VideoInput <String>
        Enable or disable video input. If not provided default is used.

    -ProtectedClient <String>
        Enable or disable protected client. If not provided default is used.

    -PrinterRedirection <String>
        Enable or disable printer redirection. If not provided default is used.

    -ClipboardRedirection <String>
        Disable clipboard redirection. If not provided default is used.

    -MemoryInMB <Int32>
        The memory to be used in MB.

    <CommonParameters>
        This cmdlet supports the common parameters: Verbose, Debug,
        ErrorAction, ErrorVariable, WarningAction, WarningVariable,
        OutBuffer, PipelineVariable, and OutVariable. For more information, see
        about_CommonParameters (https:/go.microsoft.com/fwlink/?LinkID=113216).

Uses provided configuration options to create a temporary .wsb file. Windows Sandbox is then started with this configuration. Supports all current configuration options available for Windows Sandbox.

---

## `twitterImage.js`
A script to redirect image urls from twitter to show the original image rather than one of the twitter resized versions. Simply replaces the last part of image urls with `=orig`.

---

## `txtconv.py`
A script to convert a text file from one encoding to another.

Both input and output encodings can be specified. If input encoding is not specified best guess is used. In addition one can specify line endings to use for the output file. If no specific line ending is provided, line endings are the same as in input file.

### Requirements
- `charset_normalizer`

### Usage
    txtconv [-h] [-f FROM_] [-t TO] [-l {lf,crlf,cr}] [-o OUT_FILE] [--overwrite] txt_file

positional arguments:

    txt_file              Text file to process

optional arguments:

    -h, --help            show this help message and exit
    -f FROM_, --from FROM_
                          Source encoding to convert from
    -t TO, --to TO        Target encoding to convert to
    -l {lf,crlf,cr}, --newline {lf,crlf,cr}
                          Line ending to use
    -o OUT_FILE, --out_file OUT_FILE
                          Output file
    --overwrite           Overwrite text file

Input and output encoding can be specified using `--from` and `--to` respectively. If no input encoding is specified `charset_normalizer` is used to detect it. The default output encoding is `UTF-8`. Line endings can be specified using `--newline` (Valid choices are `lf`, `crlf` and `cr`). If `--overwrite` is specified, the input file is overwritten, otherwise a new output file is created. Output file name may be provided using `--out_file`.
