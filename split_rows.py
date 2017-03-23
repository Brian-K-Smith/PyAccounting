#!/usr/bin/python3
"""Write csv file where rows from an input file matching specified criteria are split into multiple rows based on rows
and matching criteria in another input file.

Sometimes you need to clarify the details of a particular transaction using data from another source.

The script takes one required argument:
filter=Path to a csv file containing the columns: matching column a, matching regex a, comparison column a, comparison
column b, destination column(s) a, source column(s) b
split_source=Path to a csv file with data to use for performing split operation.

The script takes the following optional arguments:
input=Path to a csv file containing the designated input columns.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse
import re
import sys
from copy import deepcopy

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Split rows where a column matches a regex based on values in'
                                             ' second input.')
parser.add_argument('filter', help='Path to csv filter file with columns: matching column a, matching regex a,'
                                   'comparison column a, comparison column b, '
                                   'destination columns a (semicolon separated list), '
                                   'source columns b (semicolon separated list, order matching destinations),'
                                   'currency column a (column where the split values should add up to original)')
parser.add_argument('split', help='Secondary input file that contains data to use to split rows in primary.')
parser.add_argument('--add_imbalance', help='Correct for differences between actual and expected currency by adding an'
                                            'imbalance transaction.', action='store_true')
parser.add_argument('--input', help='Path to csv input file with column(s) to examine.'
                                    ' Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')

args = parser.parse_args()

currency_regex = re.compile('\$?\s*(-?\d+\.\d+)')

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
with open(args.input, newline='', encoding='UTF-8', closefd=close_input) as input_file,\
        open(args.split, newline='') as split_file,\
        open(args.filter, newline='') as filter_file,\
        open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    in_reader = csv.reader(input_file)
    filter_reader = csv.reader(filter_file, )
    split_reader = csv.reader(split_file)
    out_writer = csv.writer(output_file)
    # Set up filters map
    filters = []
    filter_headers = next(filter_reader)
    for filter_row in filter_reader:
        filt = {"a_match_col": int(filter_row[0]),
                "a_match_regex": re.compile(filter_row[1]),
                "a_comp_col": int(filter_row[2]),
                "b_comp_col": int(filter_row[3]),
                "a_dest_col": list(map(int, filter_row[4].split(';'))),
                "b_source_col": list(map(int, filter_row[5].split(';'))),
                "a_currency_col": int(filter_row[6])}
        filters.append(filt)
    # Set up split data map. Index by comparison column: list of lists containing the values from all of the
    # file B source columns
    split_data = {}
    split_headers = next(split_reader)
    for row in split_reader:
        for filt in filters:
            if row[filt["b_comp_col"]]:
                if row[filt["b_comp_col"]] not in split_data:
                    split_data[row[filt["b_comp_col"]]] = []
                data_list = []
                for col in filt["b_source_col"]:
                    data_list.append(row[col])
                split_data[row[filt["b_comp_col"]]].append(data_list)
    # Set up output file with input headers
    output_headers = next(in_reader)
    out_writer.writerow(output_headers)
    # Iterate through input
    row_count = 0
    for row in in_reader:
        row_count += 1
        out_row = deepcopy(row)
        row_split = False
        for filt in filters:
            match = filt["a_match_regex"].search(row[filt["a_match_col"]])
            if match:
                original_currency = float(row[filt["a_currency_col"]])
                split_currency = 0.0
                for key in split_data:
                    if row[filt["a_comp_col"]] == key:
                        for d_list in split_data[key]:
                            split_row = deepcopy(out_row)
                            col_count = 0
                            while col_count < len(filt["a_dest_col"]):
                                dest_col = filt["a_dest_col"][col_count]
                                if dest_col == filt["a_currency_col"]:
                                    match = currency_regex.match(d_list[col_count])
                                    split_string = match.group(1)
                                    split_row[dest_col] = split_string
                                    split_currency += float(split_string)
                                else:
                                    split_row[dest_col] = d_list[col_count]
                                col_count += 1
                            out_writer.writerow(split_row)
                            row_split = True
                if row_split and abs(original_currency - split_currency) > 0.001:
                    if args.add_imbalance:
                        imba_row = deepcopy(out_row)
                        col_count = 0
                        while col_count < len(filt["a_dest_col"]):
                            dest_col = filt["a_dest_col"][col_count]
                            if dest_col == filt["a_currency_col"]:
                                imba = original_currency - split_currency
                                split_row[dest_col] = "{:0.2f}".format(imba)
                            else:
                                split_row[dest_col] = "IMBALANCE"
                            col_count += 1
                        out_writer.writerow(split_row)
                    else:
                        print("ERROR: Sum of currency in split rows (${:.2f}) does not equal starting currency"
                              "(${:.2f}) at row {:d} ({})!"
                              .format(split_currency, original_currency, row_count, ",".join(row)), file=sys.stderr)
        if not row_split:
            out_writer.writerow(out_row)
