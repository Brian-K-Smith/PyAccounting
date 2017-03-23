#!/usr/bin/python3
"""Write csv file where specified column headers from an input file are modified.

The script takes one required argument:
filter=Path to a csv file containing the columns input column (zero-based index), output column header

The script takes the following optional arguments:
input=Path to a csv file containing the designated input columns.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Set headers in a csv to the specified values.')
parser.add_argument('filter', help='Path to csv filter file with columns: input column, output column header')
parser.add_argument('--input', help='Path to csv input file with header(s) to modify.'
                                    ' Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')

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
        filters.append([int(filter_row[0]), filter_row[1]])
    # Set up output file with input headers
    output_headers = next(in_reader)
    for filter in filters:
        output_headers[filter[0]] = filter[1]
    out_writer.writerow(output_headers)
    # Iterate through input
    for row in in_reader:
        out_writer.writerow(row)
