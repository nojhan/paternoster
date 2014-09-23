#!/usr/bin/env python3
#encoding: utf-8

# Licensed under the GPL version 3
# 2012 (c) nojhan <nojhan@nojhan.net>


import re
import sys
import argparse
import subprocess
import queue


def run( cmd, text, nowait=False ):
    # If there is a string formatting mark
    try:
        # put the matching text in it
        behest = cmd % tuple(text)
    except TypeError:
        # else, do not
        behest = cmd

    with open("/dev/null") as dev_null:
        if nowait:
            subprocess.Popen( behest, stdout=sys.stdout, stderr=dev_null, shell=True )
        else:
            subprocess.call(  behest, stdout=sys.stdout, stderr=dev_null, shell=True )


def call( cmd, text, nowait=False, queue=None ):
    if queue:
        queue.put( (cmd, text, nowait) )
    else:
        run( cmd, text, nowait )


def parse( text, pattern, cmd=[""], nowait=False, queue=None, capture_groups = False ):

    regex = re.compile(pattern)
    for match in regex.finditer(text):

        # If no groups are specified
        if not match.groups():
            call( cmd[0], text, nowait, queue )

        else:
            nb_groups = len(match.groups())

            if capture_groups:
                # For each group index.
                # Note that match.groups returns a tuple (thus being indexed in [0,n[),
                # but that match.start(0) refers to the whole match, the groups being indexed in [1,n].
                # Thus, we need to range in [1,n+1[.
                texts = []
                for group in range(1, nb_groups+1):
                    # If a group didn't match, there's nothing to do
                    if match.group(group) is not None:
                        texts.append( text[match.start(group):match.end(group)] )

                # Finally, call a single command with all the captured groups
                call( cmd[0], texts, nowait, queue )

            else:
                # Build a list of commands that match the number of groups,
                # If there is not enough commands, duplicate the last one.
                group_cmds = cmd + [cmd[-1]] * (nb_groups - len(cmd))

                for group in range(1, nb_groups+1):
                    # If a group didn't match, there's nothing to do
                    if match.group(group) is not None:
                        call( group_cmds[group-1], text[match.start(group):match.end(group)], nowait, queue )


def write( text, stream = sys.stdout):
    """
    Write "txt" on sys.stdout, then flush.
    """
    try:
        stream.write(text)
        stream.flush()

    # Silently handle broken pipes
    except IOError:
        try:
            stream.close()
        except IOError:
            pass


def read_parse( stream_in, stream_out, pattern, cmd, nowait = False, at_end = False, capture_groups = False ):
    """
    Read the given file-like object as a non-blocking stream
    and call the function on each item (line),
    with the given extra arguments.
    """

    if at_end:
        events = queue.Queue(0)
    else:
        events = None

    while True:
        try:
            item = stream_in.readline()
        except UnicodeDecodeError:
            continue
        except KeyboardInterrupt:
            break
        if not item:
            break

        # Write the line being processed
        write( item, stream_out )
        # Then do something
        parse(item, pattern, cmd, nowait, events, capture_groups)

    if at_end:
        while events.not_empty:
            try:
                run( *events.get_nowait() )
            except queue.Empty:
                break
 


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Call a command for each input matching a pattern.")

    parser.add_argument("pattern", metavar="REGEX", type=str, nargs=1,
            help="A regular expression")

    parser.add_argument("commands", metavar="CMD", type=str, nargs="+",
            help="The command to run if REGEX match. \
            If CMD contains a string formating placefolder (like \"%%s\"), \
            it will be replaced by the matching text. \
            Multiple commands may be specified as a list of space-separated strings. \
            Each command will then be called for each corresponding matching group within REGEX.")

    parser.add_argument("-w", "--no-wait", action="store_true",
            help="Don't wait for the end of the current command before calling the next one.")

    parser.add_argument("-e", "--end", action="store_true",
            help="Run commands at the end of the input stream.")

    parser.add_argument("-g", "--groups", action="store_true",
            help="Capture groups as arguments for the CMD, instead of running CMD for each group.\
            CMD must have as many formating placeholder as captured groups.")

    args = parser.parse_args()

    read_parse( sys.stdin, sys.stdout, args.pattern[0], args.commands, args.no_wait, args.end, args.groups )

