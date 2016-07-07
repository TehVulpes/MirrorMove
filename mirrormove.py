#!/usr/bin/env python
import inspect

import sys
import re
import os

path = '/etc/pacman.d/'
line_start = '## United States'
line_end = '^\\s*$'
filename = 'mirrorlist'
filenew = 'mirrorlist.pacnew'
comment = '^#\\s*'
uncomment = 'https.*'
help_str = """\
Usage: mirrormove.py [OPTIONS]
mirrormove uncomments specified lines from the pacman mirrorlist
The following options are available:

    -p path     Sets the path to search for mirrorlists in
                (default: {})

    -s start    Sets the regex to search for to start uncommenting lines
                (default: {})

    -e end      Sets the regex to search for to stop uncommenting lines
                (default: {})

    -f filename Sets the filename to save the new mirrorlist as
                (default: {})

    -n filenew  Sets the name for the .pacnew file
                (default: {})

    -c comment  Sets the regex to match the comment portion of a line with
                (default: {})

    -u uncomment    Sets the regex to search for in lines that should be
                uncommented
                (default: {})

    -h          Prints this help message and quits
    -?
""".format(path, line_start, line_end, filename, filenew, comment, uncomment)


def get_uncomment_indices(lines):
    matching = False

    for i in range(len(lines)):
        if matching:
            if re.match(line_end, lines[i]) is not None:
                matching = False
            elif re.search(uncomment, lines[i]) is not None:
                yield i
        else:
            if re.match(line_start, lines[i]) is not None:
                matching = True


def uncomment_lines(lines):
    print('Uncommenting the following lines...')

    for i in get_uncomment_indices(lines):
        lines[i] = re.sub(comment, '', lines[i])
        print(lines[i])

    return lines


def open_mirrorlist():
    read_filename = os.path.abspath('{}/{}'.format(path, filenew))

    if not os.path.isfile(read_filename):
        read_filename = os.path.abspath('{}/{}'.format(path, filename))

        if not os.path.isfile(read_filename):
            raise '"{}" is not a valid mirrorlist path'.format(path)

    file = open(read_filename)
    contents = file.read()
    file.close()
    return contents


def save_mirrorlist(lines):
    if hasattr(lines, '__iter__'):
        lines = '\n'.join(lines) + '\n'

    write_filename = os.path.abspath(path + '/' + filename)

    try:
        file = open(write_filename, 'w')

        file.write(lines)

        file.close()
    except (OSError, IOError) as error:
        print(error)
        print('\nerror writing to "{}"; did you run as root?'.format(write_filename))


def parse_args(argv):
    def set_path(path_):
        global path
        path = path_

    def set_line_start(line_start_):
        global line_start
        line_start = line_start_

    def set_line_end(line_end_):
        global line_end
        line_end = line_end_

    def set_filename(filename_):
        global filename
        filename = filename_

    def set_filenew(filenew_):
        global filenew
        filenew = filenew_

    def set_comment(comment_):
        global comment
        comment = comment_

    def set_uncomment(uncomment_):
        global uncomment
        uncomment = uncomment_

    def print_help():
        print(help_str)
        quit()

    arg_logic = {
        'p': set_path,
        's': set_line_start,
        'e': set_line_end,
        'f': set_filename,
        'n': set_filenew,
        'c': set_comment,
        'u': set_uncomment,
        'h': print_help,
        '?': print_help
    }

    i = 1
    while i < len(argv):
        arg = argv[i]
        i += 1

        if arg[0] == '-':
            for symbol in arg[1:]:
                if symbol not in arg_logic:
                    raise Exception('"{}" is not a recognized argument'.format(symbol))

                logic = arg_logic[symbol]
                arg_count = len(inspect.signature(logic).parameters)

                if i + arg_count > len(argv):
                    raise Exception('"{}" requires more arguments than {}'.format(symbol, argv[i:]))

                logic(*argv[i:i + arg_count])

                i += arg_count


def main(args):
    parse_args(args)

    lines = uncomment_lines(open_mirrorlist().split('\n'))
    save_mirrorlist(lines)


main(sys.argv)
