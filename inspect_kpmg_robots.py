import requests


def main() -> None:
    url = "https://kpmg.com/robots.txt"

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "InvestmentRadarResearch/0.1",
        },
    )

    print(f"HTTP durumu: {response.status_code}")
    print(f"Son adres: {response.url}")
    print(
        "İçerik türü:",
        response.headers.get("Content-Type", "Belirtilmemiş"),
    )

    response.raise_for_status()

    content = response.text

    if "<html" in content[:1000].casefold():
        raise RuntimeError(
            "robots.txt yerine HTML sayfası döndü."
        )

    sitemap_urls = []

    print("\nTARAMA KURALLARI")

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        directive, separator, value = line.partition(":")

        if not separator:
            continue

        directive = directive.strip().casefold()
        value = value.strip()

        if directive == "sitemap":
            sitemap_urls.append(value)

        elif directive in {
            "user-agent",
            "allow",
            "disallow",
            "crawl-delay",
        }:
            print(line)

    print("\nSİTE HARİTALARI")

    for sitemap_url in sorted(set(sitemap_urls)):
        print(sitemap_url)

    print(
        f"\nBulunan site haritası sayısı: "
        f"{len(set(sitemap_urls))}"
    )


if __name__ == "__main__":
    main()