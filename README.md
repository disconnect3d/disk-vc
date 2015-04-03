# Disk vacuum cleaner

Disk vacuum cleaner (disk_vc) is a small utility script written in Python to manage disk space by removing the oldest files from specified directories.

It was developed in order to remove old backup files when running out of space.

# Operating system
The script was only tested on Linux, but should also work on other operating systems. Keep in mind that the script assumes that hidden files are starting with dot (`.`).

# Python version
The script works on both Python 2 and Python 3.

# Requirements
The only requirement is [`docopt`](docopt.org) module, used for parsing arguments.

# Usage
```
Usage:
  disk_vc <space_reference_path> <space_below_%> <directories>...
    [--test] [--recursive] [--follow-links] [--use-bfree] [--remove-hidden]
  disk_vc -h | --help

Arguments:
  <space_reference_path>   Path used to check for free space
  <space_below_%>          Percentage of requested free space
  <directories>...         Directories from which old files will be deleted.
                           This MUST lie in <space_reference_path>
    
Options:
  -h --help                Show this screen
  --test                   Print file paths instead of removing them
  --recursive              Looks on subdirectories
  --follow-links           Whether to follow symlinks
  --use-bfree              Use total free space instead of available space
                           (don't use it if you don't know what it mean)
  --remove-hidden          Removes hidden files (files starting with '.')
```

# Notes
* The `--remove-hidden` option removes files starting with dot (`.`) and so is not portable (e.g. won't remove Windows hidden files for example)
* By default the script uses free space available for non privileged process value. If you want to use real free space, use the `--use-bfree` option (For more information refer to [this](http://pubs.opengroup.org/onlinepubs/009695399/basedefs/sys/statvfs.h.html)) 

# Automatization of old files removal

In order to launch the vacuum cleaner automatically (e.g. everyday at 1:00) on linux machine, use [cron](http://en.wikipedia.org/wiki/Cron).

