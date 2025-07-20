'''
Reads and processes OFX (Open Financial Exchange) files and data.

This module provides functionalities to parse OFX files from a file path or a
string, converting the financial data into a structured dictionary. It can also
be used as a runnable module to read and print an OFX file's content as a JSON
output.

Usage Examples:

1. Read OFX file from Command Line:
   Outputs the content of an OFX file as a JSON object.

   $ python -m fbpyutils.ofx --print /path/to/your/file.ofx

2. Programmatic Processing of OFX Data:
   Reads an OFX file and processes its data within a Python script.

   from fbpyutils.ofx import read_from_path
   
   ofx_file = '/path/to/your/file.ofx'
   data = read_from_path(ofx_file)
   
   if data:
       print(f"Account ID: {data.get('id')}")
       for transaction in data.get('statement', {}).get('transactions', []):
           print(
               f"  - Date: {transaction['date']}, "
               f"Amount: {transaction['amount']}, "
               f"Memo: {transaction['memo']}"
           )

3. Date Conversion for Different Formats:
   The `read` and `read_from_path` functions can return dates as native
   `datetime` objects or as ISO-formatted strings.

   from fbpyutils.ofx import read_from_path
   
   # Get dates as datetime objects (default)
   data_native = read_from_path('/path/to/your/file.ofx', native_date=True)
   
   # Get dates as ISO-formatted strings
   data_string = read_from_path('/path/to/your/file.ofx', native_date=False)
'''
from os import path
from ofxparse import OfxParser

import json
import sys
import getopt

from fbpyutils import string as strt
from fbpyutils import logging

from typing import Dict, Union

from datetime import datetime

import codecs


account_types = ['UNKNOWN', 'BANK', 'CREDIT_CARD', 'INVESTMENT']
"""
list: Maps OFX account type codes to human-readable strings.
- 0: UNKNOWN
- 1: BANK
- 2: CREDIT_CARD
- 3: INVESTMENT
"""


def format_date(x: datetime, native: bool = True) -> Union[datetime, str]:
    """Formats a datetime object into a desired output format.

    Args:
        x (datetime): The datetime object to format.
        native (bool, optional): If True, returns the native datetime object.
            If False, returns an ISO-formatted string. Defaults to True.

    Returns:
        Union[datetime, str]: The formatted datetime object or string.
            Example (string): "2023-10-27T10:00:00"
    """
    if native:
        return x
    else:
        return x.isoformat()


def read(x: str, native_date: bool = True) -> Dict:
    """Parses OFX data from a string into a dictionary.

    Args:
        x (str): A string containing the OFX data.
        native_date (bool, optional): If True, dates are returned as native
            datetime objects. If False, they are returned as ISO-formatted
            strings. Defaults to True.

    Returns:
        Dict: A dictionary containing the parsed OFX data, or an empty
              dictionary if parsing fails.
    """
    logging.Logger.debug(f"Starting read OFX data. native_date: {native_date}")
    try:
        ofx = OfxParser.parse(x)
        logging.Logger.info("OFX data parsed successfully.")
    except Exception as e:
        logging.Logger.error(f"Error parsing OFX data: {e}")
        return {}
    else:
        acct = ofx.account

        ofx_data = {
            'id': acct.account_id,
            'routing_number': acct.routing_number,
            'branch_id': acct.branch_id,
            'type': account_types[acct.type],
            'institution': {},
            'statement': {}
        }

        if acct.institution is not None:
            inst = acct.institution
            ofx_data['institution'] = {
                'fid': inst.fid,
                'organization': inst.organization.upper()
            }

        if acct.statement is not None:
            stmt = acct.statement
            ofx_data['statement'] = {
                'start_date': format_date(stmt.start_date, native_date),
                'end_date': format_date(stmt.end_date, native_date),
                'balance_date': format_date(stmt.balance_date, native_date),
                'balance': float(stmt.balance),
                'currency': stmt.currency.upper(),
                'transactions': []
            }

            if len(stmt.transactions) > 0:
                if acct.type in (1, 2):
                    i = 0
                    for transaction in stmt.transactions:
                        trn = {
                            'payee': transaction.payee,
                            'type': transaction.type.upper(),
                            'date': format_date(transaction.date, native_date),
                            'amount': float(transaction.amount),
                            'id': strt.hash_string('~'.join([
                                acct.account_id,
                                acct.routing_number,
                                format_date(stmt.start_date, False),
                                format_date(stmt.end_date, False),
                                str(i)])),
                            'memo': transaction.memo.upper(),
                            'sic': transaction.sic,
                            'mcc': transaction.mcc,
                            'checknum': transaction.checknum
                        }
                        ofx_data['statement']['transactions'].append(trn)
                        i = i + 1

        logging.Logger.debug("Finished read OFX data successfully.")
        return ofx_data


def read_from_path(x: str, native_date: bool = True) -> Dict:
    """Reads and parses an OFX file from a given path.

    Args:
        x (str): The file path of the OFX file.
        native_date (bool, optional): If True, dates are returned as native
            datetime objects. If False, they are returned as ISO-formatted
            strings. Defaults to True.

    Returns:
        Dict: A dictionary with the parsed OFX data, or an empty dictionary
              if the file is not found or an error occurs.
    """
    logging.Logger.debug(f"Starting read_from_path for file: {x}, native_date: {native_date}")
    try:
        with codecs.open(x, 'r') as f:
            ofx_data = read(f.read(), native_date)
        logging.Logger.info(f"Successfully read OFX data from file: {x}")
        return ofx_data
    except FileNotFoundError:
        logging.Logger.error(f"OFX file not found: {x}")
        return {}
    except OSError as e:
        logging.Logger.error(f"OS error when reading OFX file {x}: {e}")
        return {}
    except Exception as e:
        logging.Logger.error(f"An unexpected error occurred while reading OFX file {x}: {e}")
        raise

# ----

def main(argv):
    """Main function to handle command-line execution.

    Parses command-line arguments to read an OFX file and print its
    contents as a JSON object.

    Args:
        argv (list): A list of command-line arguments.
                     Expected: ['--print', '/path/to/file.ofx']
    
    Usage:
        python -m fbpyutils.ofx --print <file_path>
        python -m fbpyutils.ofx --help
    """
    logging.Logger.info("OFX module main function started.")
    helper_msg = 'Use: python -m fbpyutils.ofx --print <file_path>'
    source_path = ''

    opts, args = [], []
    try:
        opts, args = getopt.getopt(argv, '', ['print=', 'help'])
    except getopt.GetoptError:
        logging.Logger.error(f"Invalid command line option. {helper_msg}")
        print(helper_msg)
        sys.exit(2)

    if not opts:
        logging.Logger.warning("No options provided. Displaying helper message and exiting.")
        print(helper_msg)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--help':
            logging.Logger.info("Help option requested. Displaying helper message and exiting.")
            print(helper_msg)
            sys.exit(0)
        elif opt == '--print':
            source_path = arg
            logging.Logger.debug(f"Print option selected. Source path: {source_path}")

    if not source_path and not any(opt[0] == '--help' for opt in opts):
        logging.Logger.error(f"No source path provided for --print option. {helper_msg}")
        print(helper_msg)
        sys.exit(2)

    if source_path:
        if path.exists(source_path):
            logging.Logger.info(f"Processing OFX file: {source_path}")
            try:
                ofx_data = read_from_path(source_path, native_date=False)
                print(json.dumps(ofx_data, sort_keys=True, indent=4))
                logging.Logger.info(f"Successfully processed and printed OFX data from {source_path}.")
                sys.exit(0)
            except Exception as e:
                error_msg = 'Invalid or corrupted file: %s' % (source_path.split(path.sep)[-1])
                logging.Logger.error(f"{error_msg}. Exception: {e}")
                print(error_msg)
                sys.exit(2)
        else:
            logging.Logger.error(f"File not found: {source_path}")
            print('File not found.')
            sys.exit(2)
    logging.Logger.info("OFX module main function finished.")


if __name__ == '__main__':
    main(sys.argv[1:])
