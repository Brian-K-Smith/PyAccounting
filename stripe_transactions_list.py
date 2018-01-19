#!/usr/bin/python3
"""Retrieve all Stripe transactions after a start datetime (default: start of prior month) and before an end datetime (default: current) and write them to a csv file.

The script takes two required arguments:
api_key=The Stripe API key to use in this script.
api_version=The Stripe API version to use in this script.

The script takes the following optional arguments:
start_date=YYYYMMDDHHmm
end_date=YYYYMMDDHHmm
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import stripe
import csv
import argparse
import arrow

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Retrieve Stripe transactions.')
parser.add_argument('api_key', help='The Stripe API key to use to retrieve the desired information')
parser.add_argument('api_version', help='The Stripe API version to use to retrieve the desired information')
parser.add_argument('start_date', help='The starting time for the desired data.', nargs='?')
parser.add_argument('end_date', help='The ending time for the desired data.', nargs='?')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')

args = parser.parse_args()

# Take care of any default setup needed
if args.start_date is None:
    args.start_date = arrow.utcnow().replace(day=1, hour=0, minute=0, second=0).shift(months=-1)
else:
    args.start_date = arrow.get(args.start_date, 'YYYYMMDDHHmm')
if args.end_date is None:
    args.end_date = arrow.utcnow()
else:
    args.end_date = arrow.get(args.end_date, 'YYYYMMDDHHmm')
close_output = True
if args.output is None:
    close_output = False
    args.output = 1

stripe.api_key = args.api_key
stripe.api_version = args.api_version

# Open required files
# noinspection PyTypeChecker
with open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    transactions = stripe.BalanceTransaction.list(created=
                                                  {"gte": args.start_date.timestamp, "lte": args.end_date.timestamp})

    out_writer = csv.writer(output_file)
    # Set up output file with headers
    out_writer.writerow(["id", "amount", "available_on", "created", "currency", "description", "fee", "net", "source",
                         "status", "type"])
    for trans in transactions.auto_paging_iter():
        out_writer.writerow([trans.id, "${:6.2f}".format(trans.amount / 100), trans.available_on, trans.created,
                             trans.currency, trans.description, "${:6.2f}".format(trans.fee / 100),
                             "${:6.2f}".format(trans.net / 100), trans.source, trans.status, trans.type])
