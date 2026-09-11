from app.crawler.pdf_discovery import discover_pdf_urls


def test_converts_old_author_link_to_public_candidate():
    html = """
    <a href="https://author.kpmg.com/content/dam/kpmg/tr/pdf/2023/05/report.pdf">
        İndir
    </a>
    """

    result = discover_pdf_urls(
        html,
        "https://kpmg.com/tr/tr/report.html",
    )

    assert result == [
        "https://assets.kpmg.com/content/dam/kpmgsites/"
        "tr/pdf/2023/05/report.pdf"
    ]


def test_preserves_existing_public_link():
    url = (
        "https://assets.kpmg.com/content/dam/kpmgsites/"
        "tr/pdf/2026/06/report.pdf"
    )

    result = discover_pdf_urls(
        f'<a href="{url}">İndir</a>',
        "https://kpmg.com/tr/tr/report.html",
    )

    assert result == [url]


def test_does_not_convert_unrelated_author_path():
    html = """
    <a href="https://author.kpmg.com/private/report.pdf">
        İndir
    </a>
    """

    assert discover_pdf_urls(
        html,
        "https://kpmg.com/tr/tr/report.html",
    ) == []


def test_deduplicates_direct_and_converted_links():
    html = """
    <a href="https://author.kpmg.com/content/dam/kpmg/tr/pdf/2023/05/report.pdf">
        Eski bağlantı
    </a>
    <a href="https://assets.kpmg.com/content/dam/kpmgsites/tr/pdf/2023/05/report.pdf">
        Yeni bağlantı
    </a>
    """

    result = discover_pdf_urls(
        html,
        "https://kpmg.com/tr/tr/report.html",
    )

    assert len(result) == 1