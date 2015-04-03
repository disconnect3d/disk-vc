"""Manage disk space by removing the oldest files in specified directories.

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
"""

from __future__ import division

from docopt import docopt
import time
import os
import sys
import logging


def is_hidden_file(file_name):
    return file_name.startswith('.')


def get_file_stats(file_path):
    """Returns file path, size, and last modified date in seconds and humanized form."""
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file_path)
    return file_path, size, mtime, time.ctime(mtime)


def get_files_with_stats(search_path, recursive=False, follow_links=False, remove_hidden=False):
    files_with_stats = []

    for dir_path, dir_names, file_names in os.walk(search_path, followlinks=follow_links):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)

            if not remove_hidden and is_hidden_file(file_name):
                continue

            # Omitting files that are links and can't be accessed
            # For example ~/.config/google-chrome/SingletonLock
            # lrwxrwxrwx  1 dc dc       7 mar 27 10:33 SingletonLock -> dc-2931
            if os.path.isfile(file_path):
                files_with_stats.append(get_file_stats(file_path))

        if not recursive:
            break

    return files_with_stats


def get_disk_space(path, use_real_free_space=False):
    statvfs = os.statvfs(path)

    total = statvfs.f_blocks * statvfs.f_frsize
    free = statvfs.f_bfree * statvfs.f_frsize
    available = statvfs.f_bavail * statvfs.f_frsize

    return {
        'total': total,
        'free': free if use_real_free_space else available,
        'used': total - available
    }


def is_valid_size(free_space_percentage, disk_space_threshold):
    return disk_space_threshold < free_space_percentage


def humanized_size(size):
    for val, ext in ((10 ** 9, 'GB'), (10 ** 6, 'MB'), (10 ** 3, 'KB'), (0, 'B')):
        if size >= val:
            rounded = round(size / val, 2) if val else size
            return "{}{}".format(rounded, ext)


if __name__ == '__main__':
    args = docopt(__doc__)

    path_on_disk = args['<space_reference_path>']
    disk_space_threshold = float(args['<space_below_%>'])
    directories = args['<directories>']

    testing = args['--test']
    recursive = args['--recursive']
    follow_links = args['--follow-links']
    use_bfree = args['--use-bfree']
    remove_hidden = args['--remove-hidden']

    logging.basicConfig(format='%(asctime)-15s %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel('INFO')

    disk_space = get_disk_space(path_on_disk, use_bfree)
    free_space_percentage = (disk_space['free'] / disk_space['total']) * 100

    if disk_space_threshold < free_space_percentage:
        logger.info("There is more free space ({:.4}% => {} / {}) on disk than the passed threshold."
                    .format(free_space_percentage, humanized_size(disk_space['free']), humanized_size(disk_space['total'])))
        sys.exit()

    else:
        errors = ''
        for directory in directories:
            if not os.path.isdir(directory):
                errors += 'path: {} does not exist.\n'.format(directory)

        if errors:
            logger.error("ERRORS:\n{}".format(errors))
            sys.exit()

        files_with_stats = []
        for directory in directories:
            files = get_files_with_stats(search_path=directory,
                                         recursive=recursive,
                                         follow_links=follow_links,
                                         remove_hidden=remove_hidden)
            files_with_stats.extend(files)

        files_with_stats = sorted(files_with_stats, key=lambda i: i[2])

        clean_done = False

        for file_path, size, mtime, human_time in files_with_stats:
            logger.info("Removing file {} (size={}, time={})".format(file_path, humanized_size(size), human_time))

            if not testing:
                os.remove(file_path)
                disk_space = get_disk_space(path_on_disk, use_bfree)
            else:
                disk_space['free'] += size

            free_space_percentage = 100.0 * disk_space['free'] / disk_space['total']

            if is_valid_size(free_space_percentage, disk_space_threshold):
                logger.info("New free space: {:.4}% => {} / {}".format(free_space_percentage,
                                                                       humanized_size(disk_space['free']),
                                                                       humanized_size(disk_space['total'])))
                clean_done = True
                break

        if not clean_done:
            logger.info("Couldn't cleanup <directories> into {:.4}% free space.\n".format(disk_space_threshold) +
                        "New free space: {:.4}% => {} / {}".format(free_space_percentage,
                                                                   humanized_size(disk_space['free']),
                                                                   humanized_size(disk_space['total'])))

