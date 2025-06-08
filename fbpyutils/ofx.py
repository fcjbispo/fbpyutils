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

import codecs


account_types = ['UNKNOWN', 'BANK', 'CREDIT_CARD', 'INVESTMENT']


def format_date(x: datetime, native: bool = True) -> Union[datetime, str]:
    """
    Formats a datetime for use in ofx data.
     Args:
        x (datetime): The datetime to be used.
        native (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Union[datetime, str]: The datetime formatted to be used in dict or string iso format.
            Example: "2020-03-10T03:00:00"
    """
    if native:
        return x
    else:
        return x.isoformat()


def read(x: str, native_date: bool = True) -> Dict:
    """
    Reads ofx data into a dictionary.
     Args:
        x (str): The ofx data.
        native_date (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Dict: A dictionary with the ofx data.
    """
    try:
        ofx = OfxParser.parse(x)
    except Exception:
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

        return ofx_data


def read_from_path(x: str, native_date: bool = True) -> Dict:
    """
    Reads ofx data from a file into a dictionary.
     Args:
        x (str): The ofx file path to be read.
        native_date (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Dict: A dictionary with the ofx data.
    """
    try:
        f = codecs.open(x)
    except OSError:
        return {}
    else:
        ofx_data = read(f, native_date)
        f.close()
        return ofx_data

# ----

def main(argv):
    """
    Main function of the program.
     Parameters:
    - argv (list): A list of command-line arguments passed to the program.
     Returns:
    None
     Functionality:
    - Parses the command-line arguments using getopt.
    - If no arguments are provided or an invalid option is used, it prints a helper message and exits.
    - If the "--print" option is used, it sets the source_path variable to the provided argument.
    - If the source_path exists, it reads data from the file using the read_from_path function.
    - It then prints the data as a JSON string.
    - If an exception occurs during the process, it prints an error message indicating an invalid or corrupted file.
    - If the source_path does not exist, it prints a "File not found" message.
     Note:
    - The read_from_path function is not defined in the provided code snippet and should be implemented separately.
     Example Usage:
    $ python ofx.py --print myfile.ofx
     This will read the data from "myfile.ofx" and print it as a formatted JSON string.
    """
    helper_msg = 'Use ofx.py --print <file_path>'
    source_path = ''

    opts, args = [], []
    try:
        opts, args = getopt.getopt(argv, '', ['print=', 'help'])
    except getopt.GetoptError:
        print(helper_msg)
        sys.exit(2)

    if not opts: # Se não houver opções, imprime a mensagem de ajuda e sai
        print(helper_msg)
        sys.exit(2)
        return # Garante que o código não continue

    for opt, arg in opts:
        if opt == '--help':
            print(helper_msg)
            sys.exit(0) # Saída com 0 para ajuda
            return # Garante que o código não continue
        elif opt == '--print':
            source_path = arg

    # Verifica se source_path foi definido APÓS o loop de opções
    # Se --help foi usado, o return anterior já terá saído.
    # Se --print foi usado sem argumento, ou outra opção inválida, getopt já deu erro.
    # Esta verificação agora cobre o caso de --print não ser a opção fornecida.
    if not source_path and not any(opt[0] == '--help' for opt in opts):
        print(helper_msg)
        sys.exit(2)
        return

    if source_path: # Prossiga apenas se source_path estiver definido
        if path.exists(source_path):
            try:
                ofx_data = read_from_path(source_path, native_date=False)
                print(json.dumps(ofx_data, sort_keys=True, indent=4))
                sys.exit(0) # Saída com 0 para sucesso
            except Exception:
                print('Invalid or corrupted file: %s' % (source_path.split(path.sep)[-1]))
                sys.exit(2) # Saída com 2 para erro de arquivo
        else:
            print('File not found.')
            sys.exit(2)
    # Se chegou aqui, significa que --help foi processado ou um erro já ocorreu e sys.exit foi chamado.
    # Não é necessário um sys.exit(0) explícito aqui, pois os caminhos de sucesso já o fazem.


if __name__ == '__main__':
    main(sys.argv[1:])
