from app.crawler.report_discovery import discover_report_urls


def test_discovers_startup_investment_report_urls():
    html = """
    <html>
        <body>
            <a href="/tr/tr/insights/normal-bir-yayin.html">
                Normal Bir Yayın
            </a>

            <a href="/tr/tr/insights/2026/06/turkiye-startup-yatirimlari-2026.html">
                Türkiye Startup Yatırımları 2026
            </a>

            <a href="/tr/tr/insights/2026/06/turkiye-startup-yatirimlari-2026.html">
                Detaylar için tıklayın
            </a>
        </body>
    </html>
    """

    result = discover_report_urls(
        html=html,
        base_url="https://kpmg.com",
    )

    assert result == [
        "https://kpmg.com/tr/tr/insights/2026/06/"
        "turkiye-startup-yatirimlari-2026.html"
    ]


def test_returns_empty_list_when_no_report_exists():
    html = """
    <html>
        <body>
            <a href="/tr/tr/insights/vergi.html">
                Vergi Araştırması
            </a>
        </body>
    </html>
    """

    result = discover_report_urls(
        html=html,
        base_url="https://kpmg.com",
    )

    assert result == []