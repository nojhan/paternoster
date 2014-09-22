#!/usr/bin/env python3
#encoding: utf-8

# Licensed under the GPL version 3
# 2012 (c) nojhan <nojhan@nojhan.net>


import re
import sys
import argparse
import subprocess


def call( cmd, text, nowait=False ):

    # If there is a string formatting mark
    try:
        # put the matching text in it
        behest = cmd % text
    except TypeError:
        # else, do not
        behest = cmd

    with open("/dev/null") as dev_null:
        if nowait:
            subprocess.Popen( behest, stdout=sys.stdout, stderr=dev_null, shell=True )
        else:
            subprocess.call(  behest, stdout=sys.stdout, stderr=dev_null, shell=True )


def parse( text, pattern, cmd=[""], nowait=False ):

    regex = re.compile(pattern)
    for match in regex.finditer(text):

        # If no groups are specified
        if not match.groups():
            call( cmd[0], text, nowait )

        else:
            nb_groups = len(match.groups())

            # Build a list of colors that match the number of grouped,
            # If there is not enough commands, duplicate the last one.
            group_cmds = cmd + [cmd[-1]] * (nb_groups - len(cmd))

            # For each group index.
            # Note that match.groups returns a tuple (thus being indexed in [0,n[),
            # but that match.start(0) refers to the whole match, the groups being indexed in [1,n].
            # Thus, we need to range in [1,n+1[.
            for group in range(1, nb_groups+1):
                # If a group didn't match, there's nothing to do
                if match.group(group) is not None:
                    call( group_cmds[group-1], text[match.start(group):match.end(group)], nowait )


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


def map_write( stream_in, stream_out, function, *args ):
    """
    Read the given file-like object as a non-blocking stream
    and call the function on each item (line),
    with the given extra arguments.

    A call to "map_write(sys.stdin, function, *args)" will translate to the
    non-blocking equivalent of:
        for item in sys.stdin.readlines():
            write( function( *args ) )
    """
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
        # Then do something (blocking)
        function(item, *args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Call a command for each input matching a pattern.")

    parser.add_argument("pattern", metavar="REGEX", type=str, nargs=1,
            help="A regular expression")

    parser.add_argument("commands", metavar="CMD", type=str, nargs="+",
            default="espeak %s",
            help="The command to run if REGEX match. \
            If CMD contains a string formating placefolder (like \"%%s\"), \
            it will be replaced by the matching text. \
            Multiple commands may be specified as a list of space-separated strings. \
            Each command will then be called for each corresponding matching group within REGEX.")

    parser.add_argument("-w", "--no-wait", action="store_true",
            help="Don't wait for the end of the current command before calling the next one.")

    args = parser.parse_args()

    map_write( sys.stdin, sys.stdout, parse, args.pattern[0], args.commands, args.no_wait )

