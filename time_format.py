#!/usr/bin/python3
"""Write csv file where date/time columns in input file are manipulated and written to a new column in an output file.

Spreadsheets are terrible at doing useful things with dates and times.

The script takes one required argument:
filter=Path to a csv file containing the columns input column, date/time/datetime, input format, output format,
       output header. The input and output format are as described here: http://arrow.readthedocs.io/en/latest/#tokens

The script takes the following optional arguments:
input=Path to a csv file containing at minimum the columns payee, category, subcategory. The first row should contain
column headers.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse
import re
import arrow

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Add a column with a modified date/time to a csv.')
parser.add_argument('filter', help='Path to csv filter file with columns: input column, input format,'
                                   'output format, output header')
parser.add_argument('--input', help='Path to csv input file with a date, time, or datetime in the designated column(s).'
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
        filters.append([int(filter_row[0]), re.compile(filter_row[1]), filter_row[2].split(' ')])
    # Set up output file with input headers and headers added by each regex
    output_headers = next(in_reader)
    for filt in filters:
        output_headers.append(filt[3])
    out_writer.writerow(output_headers)
    # Iterate through input
    for row in in_reader:
        out_row = row
        # Perform each of the requested datetime operations on this row
        for filt in filters:
            in_datetime = arrow.get(filt[0], row[filt[1]])
            out_row.append(in_datetime.format(filt[2]))
        out_writer.writerow(out_row)
