import pytest

from app.crawler.report_url_filter import is_investment_report_url


@pytest.mark.parametrize(
    "url",
    [
        (
            "https://kpmg.com/tr/tr/insights/2024/02/"
            "turkiye-startup-yatirimlari-2023.html"
        ),
        (
            "https://kpmg.com/tr/tr/insights/2025/02/"
            "kpmg_turkiye_startup_yatirimlari_2024.html"
        ),
        (
            "https://kpmg.com/tr/tr/insights/2023/05/"
            "turkish-startup-investments-review.html"
        ),
    ],
)
def test_accepts_investment_report_candidates(url):
    assert is_investment_report_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        (
            "https://kpmg.com/tr/tr/insights/2024/04/"
            "kpmg--tuerkiye-deki-startup-lar-duenya-sahnesine-tayor-.html"
        ),
        (
            "https://example.com/tr/tr/insights/"
            "turkiye-startup-yatirimlari.html"
        ),
        (
            "https://kpmg.com/us/en/insights/"
            "turkish-startup-investments-review.html"
        ),
    ],
)
def test_rejects_unrelated_urls(url):
    assert is_investment_report_url(url) is False