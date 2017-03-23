#!/usr/bin/python3
"""Take a csv with stripe transfer ids and output a csv with all transactions for all transfers.

The script takes three required arguments:
api_key=The Stripe API key to use in this script.
api_version=The Stripe API version to use in this script.
column=The column in the input file where the transfer ids are located.

The script takes the following optional arguments:
input=Path to a csv file containing the designated input columns.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import stripe
import csv
import argparse
import sys

from copy import deepcopy

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Retrieve transactions included in stripe transfers at column.')
parser.add_argument('api_key', help='The Stripe API key to use to retrieve the desired information')
parser.add_argument('api_version', help='The Stripe API version to use to retrieve the desired information')
parser.add_argument('column', help='Zero-based index of column with transfer ids.')
parser.add_argument('--input', help='Path to csv input file with column(s) to examine.'
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

stripe.api_key = args.api_key
stripe.api_version = args.api_version

# Open required files
# noinspection PyTypeChecker
with open(args.input, newline='', encoding='UTF-8', closefd=close_input) as input_file,\
        open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    in_reader = csv.reader(input_file)
    out_writer = csv.writer(output_file)
    # Set up output file with input headers
    output_headers = next(in_reader)
    output_headers.append("transaction_ids")
    out_writer.writerow(output_headers)
    # Iterate through input
    for row in in_reader:
        transfer_id = row[int(args.column)]
        try:
            transactions = stripe.BalanceTransaction.all(transfer=transfer_id, limit=100)
            while len(transactions.data) > 0:
                for trans in transactions:
                    out_row = deepcopy(row)
                    out_row.append(trans.source)
                    out_writer.writerow(out_row)
                transactions = stripe.BalanceTransaction.all(transfer=transfer_id, limit=100,
                                                             starting_after=transactions.data[len(transactions.data) - 1].id)
        except stripe.error.InvalidRequestError:
            print("WARN: Could not find details for transfer {}.".format(transfer_id),file=sys.stderr)
