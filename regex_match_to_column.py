#!/usr/bin/python3
"""Write csv file where specified columns have a regex applied and then a new column is made from each matched group.

This script is intended to assist in categorization of product orders where the short and useful SKU string is
embedded in a much longer descriptive string.

The script takes one required argument:
filter=Path to a csv file containing the columns column, regex, and headers. The regex value is used with the match
function on the designated column (as zero-based integer) of each input row. A column is added for each item in the
space-separated list of headers and the regex match groups are placed into the added columns (blank when no match
occurs).

The script takes the following optional arguments:
input=Path to a csv file to read data from. The first row should contain column headers.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
findall=Use the supplied regular expressions in findall mode, where it is used to find all non-overlapping matches,
        outputting a semicolon-separated list in the designated column.
"""
import csv
import argparse
import re

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Add columns to a csv file based on the results of a regular expression'
                                             'applied to particular input columns.')
parser.add_argument('filter', help='Path to csv filter file with columns: column, regex, headers')
parser.add_argument('--input', help='Path to csv input file. Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')
parser.add_argument('--findall', help='Operate in findall mode', action='store_true')

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
        filters.append([int(filter_row[0]), re.compile(filter_row[1]), filter_row[2].split(' ')])
    # Set up output file with input headers and headers added by each regex
    output_headers = next(in_reader)
    for filt in filters:
        for header in filt[2]:
            output_headers.append(header)
    out_writer.writerow(output_headers)
    # Iterate through input
    for row in in_reader:
        out_row = row
        # Perform each of the requested regex matches on this row
        for filt in filters:
            if args.findall:
                matches = filt[1].findall(row[filt[0]])
                group = 0
                for header in filt[2]:
                    group += 1
                    if matches is None:
                        out_row.append("")
                    else:
                        if filt[1].groups == 1:
                            out_row.append(";".join(matches))
                        else:
                            grp_matches = []
                            for m in matches:
                                grp_matches.append(m[group])
                            out_row.append(";".join(grp_matches))
            else:
                match = filt[1].match(row[filt[0]])
                group = 0
                for header in filt[2]:
                    group += 1
                    if match is None:
                        out_row.append("")
                    else:
                        out_row.append(match.group(group))
        out_writer.writerow(out_row)
