#!/usr/bin/env python
# logging = global

import logging
import argparse
import datetime
import time
import os
import signal
import sys

__author__ = "LEllingwood"
# global variables
exit_flag = False

signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))

# logger = local instance of logging for dirwatcher.py
logger = logging.getLogger(__file__)


def find_text(filename, starting_line, search_text):
    """function looks for the 'magic' text in each file collected in dictionary"""
    with open(filename) as f:
        # corner case for empty files.
        i = 0
        for i, line in enumerate(f):
            if i > starting_line - 1:
                if search_text in line:
                    logger.info('{} found in {} at {}'.format(
                        search_text, filename, i + 1))
        return i + 1


def watch_directory(args):
    """looks through the directory for files with the given extension.  logs message when file is added and deleted.  calls the text search function"""
    watching_files = {}
    # filename will be the key, the last line read will be the value
    logger.info('Watching Directory: {}, File Extension: {}, For text: {}, at interval: {}'.format(
        args.directory, args.extension, args.words, args.interval))

    while not exit_flag:
        logger.info('while loop')
        try:
            files_list = os.listdir(args.directory)
            # synchronizing watch dictionary with watch folder.
            for file in files_list:
                if file.endswith(args.extension):
                    if file not in watching_files:
                        watching_files[file] = 0
                        logger.info('{} added to {}'.format(
                            file, args.directory))

            for file in watching_files.keys():
                if file not in files_list:
                    del watching_files[file]
                    logger.info('{} was deleted from {}'.format(
                        file, args.directory))

            # reporting magic text, if it exists in a file, update entry
            for file in watching_files:
                full_path = os.path.join(args.directory, file)
                watching_files[file] = find_text(
                    full_path, watching_files[file], args.words)

        except Exception as e:
            logger.error('unhandled exception: ' + str(e))
        time.sleep(args.interval)
    logger.info('done with while loop')
    # add graceful exit code above ('clean up time'), etc. 


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the signal name (the python2 way)

    logger.warn('Received ' + signames[sig_num])
    global exit_flag
    exit_flag = True


def create_parser():
    """creates parser for given arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--extension', default='.txt',
                        help="extension to be searched for")
    parser.add_argument('-int', '--interval', type=float,
                        default=1.0, help="interval search")
    parser.add_argument('directory',
                        help="directory to be watched")
    parser.add_argument('words',
                        help="text being sought")
    return parser


def main():
    # sets up logger. basicConfig passes info to terminal rather than log file
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s [%(threadName)-12s] %(message)s',
        datefmt='%Y-%m-%d %H:%M%S')

    # set logging level of detection
    logger.setLevel(logging.DEBUG)

    parser = create_parser()
    args = parser.parse_args()

    if not args:
        # automatically generates an error message:
        parser.print_usage()
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # timestamp to gauge when the timer started
    app_start_time = datetime.datetime.now()

    # logs message at startup
    logger.info(
        '\n'
        '_________________________________________\n'
        '       Running {0}\n'
        '       Started {1}\n'
        '_________________________________________\n'
        .format(__file__, app_start_time.isoformat()))

    watch_directory(args)

    # tracks how long the application has been running
    uptime = datetime.datetime.now() - app_start_time

    # logs message at shut down
    logger.info(
        '\n'
        '_________________________________________\n'
        '       Stopped {0}\n'
        '       Uptime was {1} \n'
        '_________________________________________\n'
        .format(__file__, str(uptime)))


if __name__ == '__main__':
    main()
