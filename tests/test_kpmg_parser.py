import pytest

from app.parser.kpmg_parser import parse_investment_records
from app.parser.exceptions import InvestmentTableNotFoundError

def test_parse_investment_records():
    html = """
    <html>
        <body>
            <table>
                <tr>
                    <th>Sıralama</th>
                    <th>Hedef Şirket</th>
                    <th>Sektör</th>
                    <th>Yatırımcı</th>
                    <th>Yatırımcı Ülkesi</th>
                    <th>Hisse (%)</th>
                    <th>İşlem Değeri ($m)</th>
                    <th>Yatırım Aşaması</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Test Robotics</td>
                    <td>Robotik</td>
                    <td>Test Ventures</td>
                    <td>Türkiye</td>
                    <td>Açıklanmadı</td>
                    <td>5,5</td>
                    <td>Erken Aşama</td>
                </tr>
                <tr>
                  <td>2</td>
                    <td>Example AI</td>
                    <td>Yapay Zekâ</td>
                    <td>Example Capital</td>
                    <td>ABD</td>
                    <td>Açıklanmadı</td>
                    <td>2,0</td>
                    <td>Tohum Aşaması</td>
                </tr>
            </table>
        </body>
    </html>
    """

    records = parse_investment_records(html)

    assert len(records) == 2

    assert records[0]["Hedef Şirket"] == "Test Robotics"
    assert records[0]["Sektör"] == "Robotik"
    assert records[0]["İşlem Değeri ($m)"] == "5,5"

    assert records[1]["Hedef Şirket"] == "Example AI"
    assert records[1]["Yatırım Aşaması"] == "Tohum Aşaması"

    def test_raises_error_when_table_is_missing():
        html = """
        <html>
            <body>
                <h1>Türkiye Startup Yatırımları</h1>
                <p>Bu sayfada tablo bulunmuyor.</p>
            </body>
        </html>
        """

        with pytest.raises(RuntimeError, match="Sayfada tablo bulunamadı"):
            parse_investment_records(html)


def test_raises_error_when_table_has_no_data_rows():
    html = """
    <html>
        <body>
            <table>
                <tr>
                    <th>Sıralama</th>
                    <th>Hedef Şirket</th>
                    <th>Sektör</th>
                    <th>Yatırımcı</th>
                    <th>Yatırımcı Ülkesi</th>
                    <th>Hisse (%)</th>
                    <th>İşlem Değeri ($m)</th>
                    <th>Yatırım Aşaması</th>
                </tr>
            </table>
        </body>
    </html>
    """

    with pytest.raises(
        RuntimeError,
        match="No data rows found in the table"
    ):
        parse_investment_records(html)

def test_raises_error_when_table_is_missing():
    html = """
    <html>
        <body>
            <h1>Türkiye Startup Yatırımları</h1>
            <p>Bu sayfada yatırım tablosu bulunmuyor.</p>
        </body>
    </html>
    """

    with pytest.raises(
            InvestmentTableNotFoundError,
            match="Investment table not found"
    ):
        parse_investment_records(html)


def test_selects_investment_table_when_multiple_tables_exist():
    html = """
    <html>
        <body>
            <table>
                <tr>
                    <th>Ay</th>
                    <th>Toplam İşlem</th>
                </tr>
                <tr>
                    <td>Ocak</td>
                    <td>50</td>
                </tr>
            </table>

            <table>
                <tr>
                    <th>Sıralama</th>
                    <th>Hedef Şirket</th>
                    <th>Sektör</th>
                    <th>Yatırımcı</th>
                    <th>Yatırımcı Ülkesi</th>
                    <th>Hisse (%)</th>
                    <th>İşlem Değeri ($m)</th>
                    <th>Yatırım Aşaması</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Test Robotics</td>
                    <td>Robotik</td>
                    <td>Test Ventures</td>
                    <td>Türkiye</td>
                    <td>Açıklanmadı</td>
                    <td>5,5</td>
                    <td>Tohum Aşaması</td>
                </tr>
            </table>
        </body>
    </html>
    """

    records = parse_investment_records(html)

    assert len(records) == 1
    assert records[0]["Hedef Şirket"] == "Test Robotics"

def test_accepts_transaction_type_header():
    html = """
    <html>
        <body>
            <table>
                <tr>
                    <th>Sıralama</th>
                    <th>Hedef Şirket</th>
                    <th>Sektör</th>
                    <th>Yatırımcı</th>
                    <th>Yatırımcı Ülkesi</th>
                    <th>Hisse (%)</th>
                    <th>İşlem Değeri ($m)</th>
                    <th>İşlem Tipi</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Example Logistics</td>
                    <td>Lojistik</td>
                    <td>Example Ventures</td>
                    <td>Türkiye</td>
                    <td>Açıklanmadı</td>
                    <td>8,5</td>
                    <td>Tohum Aşaması</td>
                </tr>
            </table>
        </body>
    </html>
    """

    records = parse_investment_records(html)

    assert len(records) == 1
    assert records[0]["İşlem Tipi"] == "Tohum Aşaması"
