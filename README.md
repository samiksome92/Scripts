# A Collection of Small Scripts

This is simply a collection of scripts to make my life easier.

## JavaScript Scripts
- [`desktopWikipedia.js`](#desktopWikipediajs)
- [`nyaaMagnet.js`](#nyaaMagnetjs)
- [`twitterImage.js`](#twitterImagejs)

## PowerShell Scripts
- [`Start-Sandbox.ps1`](#Start-Sandboxps1)

## Python Scripts
- [`fortiauth.py`](#fortiauthpy)
- [`nocache.http.server.py`](#nocachehttpserverpy)

## `desktopWikipedia.js`
A simple user script to redirect mobile english wikipedia links to their desktop versions. The script replaces `*.m.wikipedia.org` with `*.wikipedia.org` in url to achieve this.

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

## `nocache.http.server.py`
A script implementing a simple http server with custom cache control headers. Usage is same as http.server.

---

## `nyaaMagnet.js`
This script adds an extra button beside the search button in [nyaa.si](https://nyaa.si), which collects the magnet links for all of the torrents listed in the current page/screen and copies them to the clipboard.

Primary use is searching for torrents of a series and grabbing all magnet links (say for all episodes) in one go.

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
