import pytest

from app.parser.report_metadata_parser import parse_report_metadata


def test_parses_report_year_and_quarter():
    html = """
    <html>
        <body>
            <h1>Türkiye Startup Yatırımları 2026 Birinci Çeyrek</h1>
            <p>Sonuçlar açıklandı.</p>
        </body>
    </html>
    """

    result = parse_report_metadata(html)

    assert result.title == (
        "Türkiye Startup Yatırımları 2026 Birinci Çeyrek"
    )
    assert result.reporting_period == "2026-Q1"


def test_uses_title_when_h1_is_missing():
    html = """
    <html>
        <head>
            <title>Türkiye Startup Yatırımları 2025 3. Çeyrek</title>
        </head>
        <body>
            <p>Üçüncü çeyrek sonuçları</p>
        </body>
    </html>
    """

    result = parse_report_metadata(html)

    assert result.title == (
        "Türkiye Startup Yatırımları 2025 3. Çeyrek"
    )
    assert result.reporting_period == "2025-Q3"


def test_raises_error_when_year_is_missing():
    html = """
    <html>
        <body>
            <h1>Türkiye Startup Yatırımları Birinci Çeyrek</h1>
            <p>Birinci çeyrek sonuçları</p>
        </body>
    </html>
    """

    with pytest.raises(
        RuntimeError,
        match="Report year not found"
    ):
        parse_report_metadata(html)


def test_recognizes_explicit_annual_report():
    html = """
    <html>
        <body>
            <h1>Türkiye Startup Yatırımları 2025 Yıllık Değerlendirme</h1>
            <p>Yıl boyunca gerçekleşen yatırımlar.</p>
        </body>
    </html>
    """

    result = parse_report_metadata(html)

    assert result.reporting_period == "2025-FY"


def test_does_not_guess_period_from_comparison_text():
    html = """
    <html>
        <body>
            <h1>Türkiye Startup Yatırımları 2026</h1>
            <p>Geçen yılın birinci çeyreğinde yatırımlar arttı.</p>
        </body>
    </html>
    """

    with pytest.raises(
        RuntimeError,
        match="reporting period could not be determined"
    ):
        parse_report_metadata(html)

def test_known_url_does_not_override_ambiguous_title():
    html = """
    <html>
        <body>
            <h1>Türkiye Startup Yatırımları 2025</h1>
        </body>
    </html>
    """

    source_url = (
        "https://kpmg.com/tr/tr/insights/2026/03/"
        "turkiye-startup-yatirimlari-2025.html"
    )

    with pytest.raises(
        RuntimeError,
        match="reporting period could not be determined",
    ):
        parse_report_metadata(html, source_url=source_url)

@pytest.mark.parametrize(
    "title, expected_period",
    [
        (
            "Türkiye Startup Yatırımları 2024 İlk Çeyrek",
            "2024-Q1",
        ),
        (
            "Türkiye Startup Yatırımları 2024 İkinci Çeyrek",
            "2024-Q2",
        ),
    ],
)
def test_recognizes_turkish_quarter_titles(title, expected_period):
    html = f"<html><body><h1>{title}</h1></body></html>"

    result = parse_report_metadata(html)

    assert result.reporting_period == expected_period
