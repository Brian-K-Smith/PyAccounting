"""This script combines columns from multiple csv files into a single output based on a user-supplied set of rules.

The author encountered a recurring need to combine information from multiple sources to properly categorize financial
transacations."""

import csv
import argparse

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Merge columns of two csv files based on settings file.')
parser.add_argument('primary', help='Path to csv input file to which columns will be added.')
parser.add_argument('secondary', help='Path to csv input file from which columns will be duplicated.')
parser.add_argument('primary_column', help='Zero-based integer indicating which column in the primary file should be'
                                           ' matched.')
parser.add_argument('secondary_column', help='Zero-based integer indicating which column in the secondary file should'
                                             ' be checked for matches.')
parser.add_argument('merge_columns', help='One or more zero-based integers indicating which columns in the secondary'
                                          ' file should be merged into the primary when a match occurs.', nargs='+')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')

args = parser.parse_args()

# Take care of any default setup needed
close_output = True
if args.output is None:
    close_output = False
    args.output = 1

# Open required files
# noinspection PyTypeChecker
with open(args.primary, newline='', encoding='UTF-8') as primary_file,\
        open(args.output, mode='w', newline='', closefd=close_output) as output_file,\
        open(args.secondary, mode='r', newline='') as secondary_file:
    primary_reader = csv.reader(primary_file)
    secondary_reader = csv.reader(secondary_file)
    # Deal with headers
    primary_headers = next(primary_reader)
    secondary_headers = next(secondary_reader)
    output_headers = primary_headers
    for i in map(int, args.merge_columns):
        output_headers.append(secondary_headers[i])
    # Turn secondary file into dict indexed by the row to check for matches
    secondary_dict = {}
    for row in secondary_reader:
        key = row[int(args.secondary_column)]
        # if key in secondary_dict:
            # print("Row: {} will overwrite existing row {} from secondary file."
            #       .format(str(row), secondary_dict[key]))
        secondary_dict[key] = [row[i] for i in map(int, args.merge_columns)]
    # Iterate through primary file and see if there are any matches
    unmatched = []
    out_writer = csv.writer(output_file)
    out_writer.writerow(output_headers)
    for row in primary_reader:
        try:
            to_match = row[int(args.primary_column)]
            # print("Trying to find match for {}.".format(str(to_match)))
            match = secondary_dict[to_match]
            for col in match:
                row.append(col)
        except KeyError:
            # print("No match for {}.".format(row[int(args.primary_column)]))
            for i in args.merge_columns:
                row.append("")
        out_writer.writerow(row)
