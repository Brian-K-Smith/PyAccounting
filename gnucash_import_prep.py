#!/usr/bin/python3
"""Write csv file matching gnucash strict import format.

The script takes the following optional arguments:
input=Path to a csv file containing the designated input columns.
output=Path to write the output csv file. This file will be overwritten without warning if it exists.
"""
import csv
import argparse
import re
import arrow
import sys
from decimal import *

author = 'brian.k.smith@gmail.com'

parser = argparse.ArgumentParser(description='Convert imput transactions into GnuCash import format.')
parser.add_argument('--input', help='Path to csv input file with transactions.'
                                    ' Defaults to stdin.')
parser.add_argument('--output', help='Path to csv output file. This file will be overwritten if it exists. Defaults'
                                     ' to stdout.')

args = parser.parse_args()


currency_regex = re.compile('\$?\s*(-?\d+\.\d+)')
out_columns = ["Date","Transaction Type","Second Date","Account Name", "Number", "Description", "Notes", "Memo",
               "Full Category Path", "Category","Row Type","Action","Reconcile", "Amount With Sym",
               "Commodity Mnemonic","Commodity Name","Amount Num.","Rate/Price"]
account_full_name = "Assets:Current Assets:Advantis Checking"
account_name = "Advantis Checking"
out_date_col = 0
out_account_name_col = 3
out_desc_col = 5
out_full_cat_col = 8
out_cat_col = 9
out_row_type_col = 10
out_reconcile_col = 12
out_amount_with_sym_col = 13
out_commodity_mnemo_col = 14
out_commodity_name_col = 15
out_amount_col = 16
out_rate_col = 17

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
        open(args.output, mode='w', newline='', closefd=close_output) as output_file:
    in_reader = csv.reader(input_file)
    out_writer = csv.writer(output_file)
    # Deal with headers
    in_headers = next(in_reader)
    out_writer.writerow(out_columns)
    for row in in_reader:
        try:
            in_date = arrow.get(row[1], 'YYYY-MM-DD')
            out_date = in_date.format('MM/DD/YYYY')
            desc = row[0]
            dest_account_full = row[2]
            acct_parts = dest_account_full.split(":")
            dest_account_short = acct_parts[len(acct_parts) - 1]
            if row[3]:
                currency = Decimal(row[3]) * -1
            else:
                currency = Decimal(row[4])
            out_row_a = [out_date,"","", account_name,"", desc,"","", dest_account_full,dest_account_short,"T","","n",
                         "","USD","CURRENCY","",""]
            # "{:-$.2f}".format(currency)
            out_row_b = ["","","","","","","","",account_full_name,account_name,"S","","n","",
                         "USD","CURRENCY","{:.2f}".format(currency),1]
            # "{:-$.2f}".format(-1 * currency)
            out_row_c = ["", "", "", "", "", "", "", "", dest_account_full, dest_account_short, "S", "", "n",
                         "",
                         "USD", "CURRENCY", "{:.2f}".format(-1 * currency), 1]
            out_writer.writerow(out_row_a)
            out_writer.writerow(out_row_b)
            out_writer.writerow(out_row_c)
        except:
            print("ERROR: Could not process row {}.".format(", ".join(row)), file=sys.stderr)
