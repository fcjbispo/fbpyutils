import pytest
from fbpyutils import ofx
from datetime import datetime
from unittest import mock
import sys
import json


def test_format_date_native():
    dt = datetime(2025, 3, 23, 10, 30, 0)
    formatted_date = ofx.format_date(dt)
    assert formatted_date == dt

def test_format_date_iso():
    dt = datetime(2025, 3, 23, 10, 30, 0)
    formatted_date = ofx.format_date(dt, native=False)
    assert formatted_date == dt.isoformat()

@mock.patch(
    "codecs.open",
    mock.mock_open(
        read_data="""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
    <SONRS>
        <STATUS>
            <CODE>0</CODE>
            <SEVERITY>INFO</SEVERITY>
        </STATUS>
        <DTSERVER>20250323183000</DTSERVER>
        <LANGUAGE>POR</LANGUAGE>
        <FI>
            <ORG>Nome do Banco</ORG>
            <FID>12345</FID>
        </FI>
    </SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
    <STMTTRNRS>
        <TRNUID>0</TRNUID>
        <STATUS>
            <CODE>0</CODE>
            <SEVERITY>INFO</SEVERITY>
        </STATUS>
        <STMTRS>
            <CURDEF>BRL</CURDEF>
            <BANKACCTFROM>
                <BANKID>1111</BANKID>
                <ACCTID>2222</ACCTID>
                <ACCTTYPE>CHECKING</ACCTTYPE>
            </BANKACCTFROM>
            <BANKSTMTTRN>
                <TRNTYPE>DEBIT</TRNTYPE>
                <DTPOSTED>20250320</DTPOSTED>
                <TRNAMT>-100.00</TRNAMT>
                <MEMO>Saque</MEMO>
            </BANKSTMTTRN>
            <LEDGERBAL>
                <BALAMT>1000.00</BALAMT>
                <DTASOF>20250323</DTASOF>
            </LEDGERBAL>
            <AVAILBAL>
                <BALAMT>1000.00</BALAMT>
                <DTASOF>20250323</DTASOF>
            </AVAILBAL>
        </STMTRS>
    </STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""
    ),
)
@mock.patch("ofxparse.OfxParser.parse")
def test_read_from_path_valid_file(mock_ofxparse_parse):
    # Simula o retorno de OfxParser.parse
    mock_ofx_data = mock.Mock()
    mock_ofx_data.account.account_id = "2222"
    mock_ofx_data.account.routing_number = "1111"
    mock_ofx_data.account.type = 1  # BANK

    # Mock para stmt e seus atributos
    mock_stmt = mock.Mock()
    mock_stmt.start_date = datetime(2025, 3, 1)
    mock_stmt.end_date = datetime(2025, 3, 23)
    mock_stmt.balance_date = datetime(2025, 3, 23)
    mock_stmt.balance = 1000.00
    mock_stmt.currency = "BRL"
    mock_stmt.transactions = []
    mock_ofx_data.account.statement = mock_stmt

    mock_ofxparse_parse.return_value = mock_ofx_data

    file_path = "tests/valid_test.ofx"
    ofx_data = ofx.read_from_path(file_path)
    assert isinstance(ofx_data, dict)
    assert ofx_data["id"] == "2222"
    assert ofx_data["routing_number"] == "1111"
    assert ofx_data["statement"]["balance"] == 1000.00

@mock.patch("codecs.open", side_effect=OSError)
def test_read_from_path_invalid_file(mock_codecs_open):
    file_path = "tests/non_existent_test.ofx"
    ofx_data = ofx.read_from_path(file_path)
    assert ofx_data == {}

@mock.patch("ofxparse.OfxParser.parse")
def test_read_valid_data(mock_ofxparse_parse):
    # Simula o retorno de OfxParser.parse
    mock_ofx_data = mock.Mock()
    mock_ofx_data.account.account_id = "2222"
    mock_ofx_data.account.routing_number = "1111"
    mock_ofx_data.account.type = 1  # BANK

    # Mock para stmt e seus atributos
    mock_stmt = mock.Mock()
    mock_stmt.start_date = datetime(2025, 3, 1)
    mock_stmt.end_date = datetime(2025, 3, 23)
    mock_stmt.balance_date = datetime(2025, 3, 23)
    mock_stmt.balance = 1000.00
    mock_stmt.currency = "BRL"
    mock_stmt.transactions = []
    mock_ofx_data.account.statement = mock_stmt

    mock_ofxparse_parse.return_value = mock_ofx_data

    ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
    <SONRS>
        <STATUS>
            <CODE>0</CODE>
            <SEVERITY>INFO</SEVERITY>
        </STATUS>
        <DTSERVER>20250323183000</DTSERVER>
        <LANGUAGE>POR</LANGUAGE>
        <FI>
            <ORG>Nome do Banco</ORG>
            <FID>12345</FID>
        </FI>
    </SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
    <STMTTRNRS>
        <TRNUID>0</TRNUID>
        <STATUS>
            <CODE>0</CODE>
            <SEVERITY>INFO</SEVERITY>
        </STATUS>
        <STMTRS>
            <CURDEF>BRL</CURDEF>
            <BANKACCTFROM>
                <BANKID>1111</BANKID>
                <ACCTID>2222</ACCTID>
                <ACCTTYPE>CHECKING</ACCTTYPE>
            </BANKACCTFROM>
            <BANKSTMTTRN>
                <TRNTYPE>DEBIT</TRNTYPE>
                <DTPOSTED>20250320</DTPOSTED>
                <TRNAMT>-100.00</TRNAMT>
                <MEMO>Saque</MEMO>
            </BANKSTMTTRN>
            <LEDGERBAL>
                <BALAMT>1000.00</BALAMT>
                <DTASOF>20250323</DTASOF>
            </LEDGERBAL>
            <AVAILBAL>
                <BALAMT>1000.00</BALAMT>
                <DTASOF>20250323</DTASOF>
            </AVAILBAL>
        </STMTRS>
    </STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""
    ofx_data = ofx.read(ofx_content)
    assert isinstance(ofx_data, dict)
    assert ofx_data["id"] == "2222"
    assert ofx_data["routing_number"] == "1111"
    assert ofx_data["statement"]["balance"] == 1000.00

@mock.patch("ofxparse.OfxParser.parse")
def test_read_valid_data_with_transactions(mock_ofxparse_parse):
    # Simula o retorno de OfxParser.parse
    mock_ofx_data = mock.Mock()
    mock_ofx_data.account.account_id = "2222"
    mock_ofx_data.account.routing_number = "1111"
    mock_ofx_data.account.type = 1  # BANK

    # Mock para stmt e seus atributos
    mock_stmt = mock.Mock()
    mock_stmt.start_date = datetime(2025, 3, 1)
    mock_stmt.end_date = datetime(2025, 3, 23)
    mock_stmt.balance_date = datetime(2025, 3, 23)
    mock_stmt.balance = 1000.00
    mock_stmt.currency = "BRL"
    
    # Mock para transaction
    mock_transaction = mock.Mock()
    mock_transaction.payee = "Payee"
    mock_transaction.type = "CREDIT"
    mock_transaction.date = datetime(2025, 3, 20)
    mock_transaction.amount = 100.00
    mock_transaction.memo = "Memo"
    mock_stmt.transactions = [mock_transaction]
    
    mock_ofx_data.account.statement = mock_stmt

    mock_ofxparse_parse.return_value = mock_ofx_data

    ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
    <SONRS>
        <STATUS>
            <CODE>0</CODE>
            <SEVERITY>INFO</SEVERITY>
        </STATUS>
        <DTSERVER>20250323183000</DTSERVER>
        <LANGUAGE>POR</LANGUAGE>
        <FI>
            <ORG>Nome do Banco</ORG>
            <FID>12345</FID>
        </FI>
    </SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
    <STMTTRNRS>
        <TRNUID>0</TRNUID>
        <STATUS>
            <CODE>0</CODE>
            <SEVERITY>INFO</SEVERITY>
        </STATUS>
        <STMTRS>
            <CURDEF>BRL</CURDEF>
            <BANKACCTFROM>
                <BANKID>1111</BANKID>
                <ACCTID>2222</ACCTID>
                <ACCTTYPE>CHECKING</ACCTTYPE>
            </BANKACCTFROM>
            <BANKSTMTTRN>
                <TRNTYPE>DEBIT</TRNTYPE>
                <DTPOSTED>20250320</DTPOSTED>
                <TRNAMT>-100.00</TRNAMT>
                <MEMO>Saque</MEMO>
            </BANKSTMTTRN>
            <LEDGERBAL>
                <BALAMT>1000.00</BALAMT>
                <DTASOF>20250323</DTASOF>
            </LEDGERBAL>
            <AVAILBAL>
                <BALAMT>1000.00</BALAMT>
                <DTASOF>20250323</DTASOF>
            </AVAILBAL>
        </STMTRS>
    </STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""
    ofx_data = ofx.read(ofx_content)
    assert isinstance(ofx_data, dict)
    assert len(ofx_data["statement"]["transactions"]) == 1
    assert ofx_data["statement"]["transactions"][0]["payee"] == "Payee"

def test_main_valid_file(monkeypatch):
    # Simulate providing a valid file path
    monkeypatch.setattr(sys, "argv", ["ofx.py", "--print", "dummy_valid_file.ofx"])
    with mock.patch("fbpyutils.ofx.path.exists", return_value=True), \
         mock.patch("fbpyutils.ofx.read_from_path", return_value={"id": "123"}) as mock_read, \
         mock.patch("builtins.print") as mock_print, \
         mock.patch("sys.exit") as mock_exit:
        ofx.main(sys.argv[1:])
        # Check that print was called with the JSON dump of the data
        # The exact format of the JSON string can be complex to match,
        # so using mock.ANY or checking for key parts might be more robust.
        # For simplicity here, we'll assume it's called.
        mock_print.assert_any_call(json.dumps({"id": "123"}, sort_keys=True, indent=4))
        mock_exit.assert_called_with(0)

def test_main_no_arguments(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ofx.py"])
    with mock.patch("builtins.print") as mock_print, \
         mock.patch("sys.exit") as mock_exit:
        ofx.main(sys.argv[1:]) # Pass an empty list to simulate no args after script name
        mock_print.assert_any_call('Use: python -m fbpyutils.ofx --print <file_path>')
        mock_exit.assert_any_call(2)

def test_main_help_argument(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ofx.py", "--help"])
    with mock.patch("builtins.print") as mock_print, \
         mock.patch("sys.exit") as mock_exit:
        ofx.main(sys.argv[1:])
        mock_print.assert_called_with('Use: python -m fbpyutils.ofx --print <file_path>')
        mock_exit.assert_called_with(0)

def test_main_file_not_found(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ofx.py", "--print", "non_existent_file.ofx"])
    with mock.patch("fbpyutils.ofx.path.exists", return_value=False) as mock_exists, \
         mock.patch("builtins.print") as mock_print, \
         mock.patch("sys.exit") as mock_exit:
        ofx.main(sys.argv[1:])
        mock_print.assert_called_with('File not found.')
        mock_exit.assert_called_with(2)

def test_main_corrupted_file(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ofx.py", "--print", "corrupted_file.ofx"])
    with mock.patch("fbpyutils.ofx.path.exists", return_value=True) as mock_exists, \
         mock.patch("fbpyutils.ofx.read_from_path", side_effect=Exception("Corrupted file")) as mock_read, \
         mock.patch("builtins.print") as mock_print, \
         mock.patch("sys.exit") as mock_exit:
        ofx.main(sys.argv[1:])
        mock_print.assert_called_with('Invalid or corrupted file: corrupted_file.ofx')
        mock_exit.assert_called_with(2)

def test_read_invalid_data():
    invalid_ofx_content = "invalid ofx data"
    with mock.patch(
        "ofxparse.OfxParser.parse", side_effect=Exception("Parse error")
    ):
        ofx_data = ofx.read(invalid_ofx_content)
        assert ofx_data == {}
