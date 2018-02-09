#!/usr/bin/python3
"""Write a single csv file containing all rows from one or more input files

The script takes one or more required argument:
file=Path to a csv file. This argument may be present more than once.

The script takes the following optional arguments:
header_row_count=Number of header rows in all input files after the first. Header rows will not be appended. Default 1
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Concatenate multiple csv files, stripping headers.')
parser.add_argument('file', help='Path to csv filter file with columns: input column, output column header', nargs='+')
parser.add_argument('--header_row_count', help='Num rows to skip at start of files after first. Defaults to 1.',
                    default=1, type=int)
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')

args = parser.parse_args()

# Take care of any default setup needed
close_output = True
if args.output is None:
    close_output = False
    args.output = 1

# Open required files
input_file_counter = 0

# noinspection PyTypeChecker
with open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    out_writer = csv.writer(output_file)
    while input_file_counter < len(args.file):
        with open(args.file[input_file_counter], mode='r', newline='') as input_file:
            in_reader = csv.reader(input_file)
            if input_file_counter > 0:
                headers_removed = 0
                while headers_removed < args.header_row_count:
                    next(in_reader)
                    headers_removed += 1
            for row in in_reader:
                out_writer.writerow(row)
        input_file_counter += 1
