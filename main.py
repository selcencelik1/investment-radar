from app.crawler.kpmg_client import fetch_page
from app.database.investment_repository import save_investment_records
from app.parser.kpmg_parser import parse_investment_records
from app.parser.record_mapper import map_to_investment_record

url = (
    "https://kpmg.com/tr/tr/insights/2025/05/"
    "turkiye-startup-yatirimlari-2025-birinci-ceyrek.html"
)

html = fetch_page(url)
raw_records = parse_investment_records(html)

records = [
    map_to_investment_record(raw_record)
    for raw_record in raw_records
]

saved_count = save_investment_records(
    records=records,
    reporting_period="2025-Q1",
    source_url=url,
)

print(f"Bulunan kayıt: {len(records)}")
print(f"Yeni kaydedilen kayıt: {saved_count}")