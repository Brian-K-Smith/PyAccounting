#!/usr/bin/python3
"""Write csv file where payee, category, subcategory columns of input file are modified according to rules in filter.

This script is intended to assist in categorization of financial transactions retrieved from a bank website.
The author noted that no open source or commercially available consumer-level software allowed the use of regular
expressions to categorize transactions. Given the typical behavior of transaction records observed, the lack of regex
tools made categorization nearly impossible, as even transactions from the same store tended to include details about
the POS terminal and transaction number that ensured every transaction description was unique.

The script takes one required argument:
filter=Path to a csv file containing the columns regex, payee, category, subcategory. The regex value is used with the
regex search function to examine the payee column of each input row. When found, the payee, category, and subcategory
columns of the output file are set to the values in the row corresponding to the regex in the filter file.

The script takes the following optional arguments:
input=Path to a csv file containing at minimum the columns payee, category, subcategory. The first row should contain
column headers.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse
import re

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Modify payee, category, subcategory fields of a csv file based'
                                             ' on regex matching of payee.')
parser.add_argument('filter', help='Path to csv filter file with columns: regex, payee, category, subcategory')
parser.add_argument('--input', help='Path to csv input file with minimum columns: payee, category, subcategory.'
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
    in_reader = csv.DictReader(input_file)
    filter_reader = csv.DictReader(filter_file)
    # Set up filters array
    filters = []
    for filter_row in filter_reader:
        filters.append([re.compile(filter_row['regex'], re.I), filter_row['payee'],
                        filter_row['category'], filter_row['subcategory']])
    # Set up output file with input headers
    out_writer = csv.DictWriter(output_file, in_reader.fieldnames)
    out_writer.writeheader()
    # Iterate through input file
    unmatched = []
    for row in in_reader:
        original_payee = row['payee']
        # Iterate through all the regular expressions, case insensitive
        match = None
        payee = ''
        category = ''
        subcategory = ''
        for fil in filters:
            # print('Seeing if {} matches regex {}'.format(original_payee, str(filter[0])))
            result = fil[0].search(original_payee)
            if result is not None:
                # print(result)
                if match:
                    print('Payee {} previously matched {}, matched {} as well.'
                          .format(original_payee, match, str(fil[0])))
                else:
                    match = str(fil[0])
                    payee = fil[1]
                    category = fil[2]
                    subcategory = fil[3]
                # else:
                #     print('No match')
        if not match:
            unmatched.append([original_payee, row['date'], row['amount']])
        # Prepare the modified row
        out_dict = {}
        for field in in_reader.fieldnames:
            # Modify anything we need to modify
            if field == 'payee':
                if match:
                    out_dict['payee'] = payee
                else:
                    out_dict['payee'] = row['payee']
            elif field == 'category':
                if match:
                    out_dict['category'] = category
                else:
                    out_dict['category'] = row['category']
            elif field == 'subcategory':
                if match:
                    out_dict['subcategory'] = subcategory
                else:
                    out_dict['subcategory'] = row['subcategory']
            # Pass everything else through unchanged
            else:
                out_dict[field] = row[field]
        # Write out the row
        out_writer.writerow(out_dict)
    # Report things that were unmatched so user can add them to the filter
    for unmatch in unmatched:
        print('{}|{}|{}'.format(unmatch[0], unmatch[1], unmatch[2]))
