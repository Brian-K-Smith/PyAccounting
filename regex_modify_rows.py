#!/usr/bin/python3
"""Write csv file where rows from an input file matching specified criteria are modified.

Sometimes you get data that has blanks and "NULL" and six different other kinds of garbage and you need to fix it one
way or another.

The script takes one required argument:
filter=Path to a csv file containing the columns input column, regex, operation, replacement

The script takes the following optional arguments:
input=Path to a csv file containing the designated input columns.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse
import re
import sys

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Modify rows where a column matches a regex in a variety of ways.',
                                 epilog="Supported options for the operation column are:\n"
                                 "  drop    - Rows where the regex matches the input column are removed from the output.\n"
                                 "  modify - The input column in rows where the regex matches are set to the value in"
                                 " the replacement column of the filter file.\n"
                                 "  modify# - The specified column in rows where the regex matches the input column"
                                 "  are set to the value in the replacement column of the filter file.\n"
                                 "  warn    - Indicate on stderr that we found a match in a certain row.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('filter', help='Path to csv filter file with columns: input column, regex, operation,'
                                   'replacement.')
parser.add_argument('--input', help='Path to csv input file with column(s) to examine.'
                                    ' Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')
parser.add_argument('--verbose', help='Be chatty about what is happening on stderr', action='store_true')

args = parser.parse_args()

# Take care of any default setup needed
close_input = True
if args.input is None:
    close_input = False
    args.input = 0
close_output = True
if args.output is None:
    close_output = False
    args.output = 1

# Open required files
# noinspection PyTypeChecker
with open(args.input, newline='', encoding='UTF-8', closefd=close_input) as input_file, open(args.filter, newline='')\
        as filter_file, open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    in_reader = csv.reader(input_file)
    filter_reader = csv.reader(filter_file)
    out_writer = csv.writer(output_file)
    # Set up filters array
    filters = []
    filter_headers = next(filter_reader)
    for filter_row in filter_reader:
        try:
            filters.append([int(filter_row[0]), re.compile(filter_row[1]), filter_row[2], filter_row[3]])
        except IndexError:
            print("Parse error with filter row {}.".format(", ".join(filter_row)), file=sys.stderr)
    # Set up output file with input headers
    output_headers = next(in_reader)
    out_writer.writerow(output_headers)
    # Iterate through input
    row_count = 0
    for row in in_reader:
        row_count += 1
        out_row = row
        # Perform each of the requested modification operations on this row
        skip_row = False
        for filt in filters:
            match = filt[1].search(row[filt[0]])
            modifyColMatch = re.search('modify(\d+)',filt[2])
            if match:
                if filt[2] == 'warn':
                    print('row {:d} matched {} with {}'.format(row_count, filt[1].pattern, row[filt[0]]),
                          file=sys.stderr)
                elif filt[2] == 'drop':
                    skip_row = True
                    if args.verbose:
                        print('Dropping row {:d} due to match of {} with {}'.format(row_count, filt[1].pattern,
                                                                                    row[filt[0]]), file=sys.stderr)
                    break
                elif filt[2] == 'modify':
                    if args.verbose:
                        print('Setting row {:d} column {:d} to {} due to match of {} with {}'
                              .format(row_count, filt[0], filt[3], filt[1].pattern, row[filt[0]]), file=sys.stderr)
                    out_row[filt[0]] = filt[3]
                elif modifyColMatch:
                    col = int(modifyColMatch.group(1))
                    if args.verbose:
                        print('Setting row {:d} column {:d} to {} due to match of {} with {}'
                              .format(row_count, col, filt[3], filt[1].pattern, row[filt[0]]), file=sys.stderr)
                    out_row[col] = filt[3]
                else:
                    print('ERROR! Operation {} is not supported.'
                          .format(filt[2]), file=sys.stderr)
                    sys.exit(1)
        if not skip_row:
            out_writer.writerow(out_row)
