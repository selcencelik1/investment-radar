from urllib.parse import urljoin

from bs4 import BeautifulSoup


def discover_report_urls(
    html: str,
    base_url: str,
) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    discovered_urls = set()

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        link_text = link.get_text(" ", strip=True)

        normalized_href = href.casefold()
        normalized_text = link_text.casefold()

        matches_url = (
            "turkiye-startup-yatirimlari" in normalized_href
        )

        matches_text = (
            "türkiye" in normalized_text
            and "startup" in normalized_text
            and "yatırım" in normalized_text
        )

        if matches_url or matches_text:
            absolute_url = urljoin(base_url, href)

            if absolute_url.endswith(".html"):
                discovered_urls.add(absolute_url)

    return sorted(discovered_urls)