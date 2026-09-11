from decimal import Decimal

import pytest

from app.parser.kpmg_parser import parse_investment_records
from app.parser.record_mapper import map_to_investment_record


@pytest.mark.parametrize(
    "amount_header",
    ["İşlem Değeri ($m)", "İşlem Değeri (m$)"],
)
def test_parses_old_report_headers(amount_header):
    html = f"""
    <table>
        <tr>
            <th>Sıralama</th>
            <th>Girişim</th>
            <th>Sektör</th>
            <th>Yatırımcı</th>
            <th>Finansal Yatırımcı</th>
            <th>Yatırımcı Merkezi</th>
            <th>Hisse (%)</th>
            <th>{amount_header}</th>
            <th>Yatırım Aşaması</th>
        </tr>
        <tr>
            <td>1</td>
            <td>Example</td>
            <td>SaaS</td>
            <td>Example Ventures</td>
            <td>Evet</td>
            <td>Türkiye</td>
            <td>Açıklanmadı</td>
            <td>17,2</td>
            <td>Erken Aşama</td>
        </tr>
    </table>
    """

    raw_records = parse_investment_records(html)
    record = map_to_investment_record(raw_records[0])

    assert len(raw_records) == 1
    assert record.startup_name == "Example"
    assert record.investor_countries == "Türkiye"
    assert record.deal_amount_million_usd == Decimal("17.2")