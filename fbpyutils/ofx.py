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
from fbpyutils import logging

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
    """
    Reads ofx data from a file into a dictionary.
     Args:
        x (str): The ofx file path to be read.
        native_date (bool, optional): If True, use native (datetime) format to be used in dicts.
            Otherwise, uses datetime string iso format. Default is True.
     Returns:
        Dict: A dictionary with the ofx data.
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
    logging.Logger.info("OFX module main function started.")
    helper_msg = 'Use ofx.py --print <file_path>'
    source_path = ''

    opts, args = [], []
    try:
        opts, args = getopt.getopt(argv, '', ['print=', 'help'])
    except getopt.GetoptError:
        logging.Logger.error(f"Invalid command line option. {helper_msg}")
        print(helper_msg)
        sys.exit(2)

    if not opts: # Se não houver opções, imprime a mensagem de ajuda e sai
        logging.Logger.warning("No options provided. Displaying helper message and exiting.")
        print(helper_msg)
        sys.exit(2)
        return # Garante que o código não continue

    for opt, arg in opts:
        if opt == '--help':
            logging.Logger.info("Help option requested. Displaying helper message and exiting.")
            print(helper_msg)
            sys.exit(0) # Saída com 0 para ajuda
            return # Garante que o código não continue
        elif opt == '--print':
            source_path = arg
            logging.Logger.debug(f"Print option selected. Source path: {source_path}")

    # Verifica se source_path foi definido APÓS o loop de opções
    # Se --help foi usado, o return anterior já terá saído.
    # Se --print foi usado sem argumento, ou outra opção inválida, getopt já deu erro.
    # Esta verificação agora cobre o caso de --print não ser a opção fornecida.
    if not source_path and not any(opt[0] == '--help' for opt in opts):
        logging.Logger.error(f"No source path provided for --print option. {helper_msg}")
        print(helper_msg)
        sys.exit(2)
        return

    if source_path: # Prossiga apenas se source_path estiver definido
        if path.exists(source_path):
            logging.Logger.info(f"Processing OFX file: {source_path}")
            try:
                ofx_data = read_from_path(source_path, native_date=False)
                print(json.dumps(ofx_data, sort_keys=True, indent=4))
                logging.Logger.info(f"Successfully processed and printed OFX data from {source_path}.")
                sys.exit(0) # Saída com 0 para sucesso
            except Exception as e:
                error_msg = 'Invalid or corrupted file: %s' % (source_path.split(path.sep)[-1])
                logging.Logger.error(f"{error_msg}. Exception: {e}")
                print(error_msg)
                sys.exit(2) # Saída com 2 para erro de arquivo
        else:
            logging.Logger.error(f"File not found: {source_path}")
            print('File not found.')
            sys.exit(2)
    logging.Logger.info("OFX module main function finished.")


if __name__ == '__main__':
    main(sys.argv[1:])
