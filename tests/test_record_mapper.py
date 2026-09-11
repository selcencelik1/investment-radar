from decimal import Decimal

from app.models.investment_record import InvestmentRecord
from app.parser.record_mapper import map_to_investment_record


def test_maps_raw_record_to_investment_record():
    raw_record = {
        "Sıralama": "1",
        "Hedef Şirket": "Good Job Games",
        "Sektör": "Oyun",
        "Yatırımcı": "Menlo Ventures",
        "Yatırımcı Ülkesi": "ABD",
        "Hisse (%)": "Açıklanmadı",
        "İşlem Değeri ($m)": "23,0",
        "Yatırım Aşaması": "Erken Aşama"
    }

    result = map_to_investment_record(raw_record)

    assert isinstance(result, InvestmentRecord)
    assert result.ranking == 1
    assert result.startup_name == "Good Job Games"
    assert result.sector == "Oyun"
    assert result.investors == "Menlo Ventures"
    assert result.deal_amount_million_usd == Decimal("23.0")
    assert result.investment_stage == "Erken Aşama"

def test_maps_transaction_type_as_investment_stage():
    raw_record = {
        "Sıralama": "1",
        "Hedef Şirket": "Example Logistics",
        "Sektör": "Teslimat ve Lojistik",
        "Yatırımcı": "Example Ventures",
        "Yatırımcı Ülkesi": "Türkiye",
        "Hisse (%)": "Açıklanmadı",
        "İşlem Değeri ($m)": "8,5",
        "İşlem Tipi": "Tohum Aşaması",
    }

    result = map_to_investment_record(raw_record)

    assert result.investment_stage == "Tohum Aşaması"