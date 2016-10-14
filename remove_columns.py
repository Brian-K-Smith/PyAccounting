#!/usr/bin/python3
"""Write csv file where certain columns of input file are removed.

The script takes one required argument:
remove_cols=Columns (designated as zero-based integers) to remove from the input when producing the output.

The script takes the following optional arguments:
input=Path to a csv file containing at minimum the columns payee, category, subcategory. The first row should contain
column headers.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse
import re

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Remove specified columns (as zero-based integers) from a csv file.')
parser.add_argument('remove_cols', help='The columns to remove', nargs="+", type=int)
parser.add_argument('--input', help='Path to csv input file with minimum columns: payee, category, subcategory.'
                                    ' Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')
parser.add_argument('--inverse', help='Use the specified columns as a list to be included, not removed. All others'
                                      'will be removed.', action='store_true')

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

# noinspection PyTypeChecker
with open(args.input, newline='', encoding='UTF-8', closefd=close_input) as input_file,\
        open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    in_reader = csv.reader(input_file)
    out_writer = csv.writer(output_file)
    for row in in_reader:
        out_row = []
        for i in range(0, len(row)):
            if args.inverse:
                if i in args.remove_cols:
                    out_row.append(row[i])
            else:
                if i not in args.remove_cols:
                    out_row.append(row[i])
        out_writer.writerow(out_row)
