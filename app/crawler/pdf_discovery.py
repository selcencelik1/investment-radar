from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup


def discover_pdf_urls(
    html: str,
    page_url: str,
) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    pdf_urls = set()

    for link in soup.find_all("a", href=True):
        absolute_url = urljoin(
            page_url,
            link["href"].strip(),
        )
        parsed = urlsplit(absolute_url)

        if parsed.scheme not in {"http", "https"}:
            continue

        if not parsed.path.casefold().endswith(".pdf"):
            continue

        if parsed.hostname in {"kpmg.com", "assets.kpmg.com"}:
            pdf_urls.add(absolute_url)
            continue

        if (
            parsed.hostname == "author.kpmg.com"
            and parsed.path.startswith(
                "/content/dam/kpmg/tr/pdf/"
            )
        ):
            candidate_path = parsed.path.replace(
                "/content/dam/kpmg/",
                "/content/dam/kpmgsites/",
                1,
            )

            candidate_url = urlunsplit((
                "https",
                "assets.kpmg.com",
                candidate_path,
                parsed.query,
                "",
            ))

            pdf_urls.add(candidate_url)

    return sorted(pdf_urls)