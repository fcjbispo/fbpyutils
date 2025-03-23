import pytest
from fbpyutils import ofx
from datetime import datetime
from unittest import mock
import codecs


class TestOfxModule:
    def test_format_date_native(self):
        dt = datetime(2025, 3, 23, 10, 30, 0)
        formatted_date = ofx.format_date(dt)
        assert formatted_date == dt

    def test_format_date_iso(self):
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
    def test_read_from_path_valid_file(self, mock_ofxparse_parse):
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
    def test_read_from_path_invalid_file(self, mock_codecs_open):
        file_path = "tests/non_existent_test.ofx"
        ofx_data = ofx.read_from_path(file_path)
        assert ofx_data == {}

    @mock.patch("ofxparse.OfxParser.parse")
    def test_read_valid_data(self, mock_ofxparse_parse):
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

    def test_read_invalid_data(self):
        invalid_ofx_content = "invalid ofx data"
        with mock.patch(
            "ofxparse.OfxParser.parse", side_effect=Exception("Parse error")
        ):
            ofx_data = ofx.read(invalid_ofx_content)
            assert ofx_data == {}
