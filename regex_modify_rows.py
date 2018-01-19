#!/usr/bin/python3
"""Write csv file where rows from an input file matching specified criteria are modified.

Sometimes you get data that has blanks and "NULL" and six different other kinds of garbage and you need to fix it one
way or another.

The script takes one required argument:
filter=Path to a csv file containing columns: input column name, regex, operation, operation column name, operation data

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
                                 "  drop    - Rows where 'regex' matches 'input column' are removed from the output.\n"
                                 "  modify - The 'output column' in rows where 'regex' matches 'input column' are set"
                                        " to 'operation data'.\n"
                                 "  warn    - Indicate on stderr that we found a match in a certain row.\n"
                                 "  append  - Add a column named 'operation column name' to each row and put"
                                        " 'operation data' into that column when 'regex' matches 'input column'.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('filter', help='Path to csv filter file with columns: input column name, regex, operation,'
                                   'operation column, operation data. The first row is assumed to contain headers. '
                                   'Each subsequent row represents one action to perform on each row in the input file.'
                                   ' It is recommended to place drop operations at the top of the filter rows so'
                                   ' dropped rows can be skipped for the remaining operations.')
parser.add_argument('--input', help='Path to csv input file with column(s) to examine.'
                                    ' Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')
parser.add_argument('--verbose', help='Be chatty about what is happening on stderr', action='store_true')
parser.add_argument('--warn_nomatch', help='Complain on stderr if no filter matched a row', action='store_true')

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
    filter_reader = csv.DictReader(filter_file)
    out_writer = csv.writer(output_file)
    # Set up initial output file headers with input file headers
    input_headers = next(in_reader)
    output_headers = input_headers
    # Set up filters array. 0: input column name, 1: input column number, 2: regex, 3: operation, 4: operation column
    # name, 5: operation column number in output, 6: operation data
    filters = []
    filter_row_counter = 0
    for filter_row in filter_reader:
        # Add any needed new column headers
        if filter_row['operation'] == 'append':
            output_headers.append(filter_row['operation column name'])
        filters.append([filter_row['input column name'], output_headers.index(filter_row['input column name']),
                        re.compile(filter_row['regex']), filter_row['operation'],
                        filter_row['operation column name'], output_headers.index(filter_row['operation column name']),
                        filter_row['operation data']])
        filter_row_counter += 1
    # Iterate through input
    out_writer.writerow(output_headers)
    row_count = 0
    for row in in_reader:
        row_count += 1
        out_row = row
        row_dict = dict(zip(input_headers, row))
        # Perform each of the requested modification operations on this row
        skip_row = False
        match_count = 0
        for filt in filters:
            in_val = row_dict[filt[0]]
            match = filt[2].search(in_val)
            # Do the thing we were told to do when there was a match
            if match:
                match_count += 1
                if filt[3] == 'drop':
                    skip_row = True
                    if args.verbose:
                        print('Dropping row {:d} due to match of {} with {}. No other filters will be processed for'
                              ' this row.'.format(row_count, filt[2].pattern, in_val), file=sys.stderr)
                    break
                elif filt[3] == 'warn':
                    print('row {:d} matched {} with {}'.format(row_count, filt[2].pattern, in_val),
                          file=sys.stderr)
                elif filt[3] == 'modify':
                    if args.verbose:
                        print('Setting row {:d} column {} to {} due to match of {} with {}'
                              .format(row_count, filt[4], filt[6], filt[2].pattern, in_val), file=sys.stderr)
                    out_row[filt[5]] = filt[6]
                elif filt[3] == 'append':
                    if args.verbose:
                        print('Appending row {:d} with {} due to match of {} with {}'
                              .format(row_count, filt[6], filt[2].pattern, in_val), file=sys.stderr)
                    out_row.append(filt[6])
                else:
                    print('ERROR! Operation {} is not supported.'
                          .format(filt[3]), file=sys.stderr)
                    sys.exit(1)
            # Sometimes we need to do things to rows that don't match
            else:
                if filt[3] == 'append':
                    out_row.append('')
        if not skip_row:
            out_writer.writerow(out_row)
        if args.warn_nomatch and match_count == 0:
            print('No match at row {:d}: {} '.format(row_count, row), file=sys.stderr)
