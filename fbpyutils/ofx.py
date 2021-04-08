'''
Reads and processes OFX (Open Financial Exchange) files and data.

Can be used as runable module to read and print out an ofx file content
as json output:
    python -m utils.ofx --print <ofx_file_path>
'''
from os import path
from ofxparse import OfxParser

import json
import sys
import getopt

from fbpyutils import string as strt

from typing import Dict, Union

from datetime import datetime


account_types = ['UNKNOWN', 'BANK', 'CREDIT_CARD', 'INVESTMENT']


def format_date(
    x: datetime, native: bool = True
) -> Union[datetime, str]:
    '''
    Formats a datetime for use in ofx data

        x
            The datetime to be used
        native
            if True use native (datetime) format to be used in dicts.
            Else uses datetime string iso format. Default = True

        Return the datetime formatted to be used in dict or string iso format
            Ex.: "2020-03-10T03:00:00"
    '''
    if native:
        return x
    else:
        return x.isoformat()


def read(
    x: str, native_date: bool = True
) -> Dict:
    '''
    Reads ofx data into a dict

        x
            The ofx data
        native
            if True use native (datetime) format to be used in dicts.
            Else uses datetime string iso format. Default = True

        Return a dict with the ofx data
    '''
    ofx = OfxParser.parse(x)
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

    return ofx_data


def read_from_path(
    x: str, native_date: bool = True
) -> Dict:
    '''
    Reads ofx data from file into a dict

        x
            The ofx file path to be readed
        native
            if True use native (datetime) format to be used in dicts.
            Else uses datetime string iso format. Default = True

        Return a dict with the ofx data
    '''
    try:
        f = open(x, 'rb')
    except OSError:
        return {}
    else:
        ofx_data = read(f, native_date)
        f.close()
        return ofx_data

# ----

def main(argv):
    helper_msg = 'Use ofx.py --print <file_path>'
    source_path = ''

    try:
        opts, args = getopt.getopt(argv, '', ['print='])
    except getopt.GetoptError:
        print(helper_msg)
        sys.exit(2)

    if len(opts) == 0:
        print(helper_msg)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(helper_msg)
        elif opt in ('--print'):
            source_path = arg

    if path.exists(source_path):
        try:
            ofx_data = read_from_path(source_path,
                                          native_date=False)
            print(json.dumps(ofx_data, sort_keys=True, indent=4))
        except Exception:
            print('Invalid or corrupted file: %s' %
                  (source_path.split(path.sep)[-1]))
    else:
        print('File not found.')
        sys.exit(2)
    sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
