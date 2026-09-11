import requests
from defusedxml import ElementTree


SITEMAP_URL = "https://kpmg.com/sitemap-index.xml"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> None:
    response = requests.get(
        SITEMAP_URL,
        timeout=30,
        headers={
            "User-Agent": "InvestmentRadarResearch/0.1",
        },
    )

    print(f"HTTP durumu: {response.status_code}")
    response.raise_for_status()

    root = ElementTree.fromstring(response.content)

    print(f"XML türü: {local_name(root.tag)}")

    locations = sorted({
        element.text.strip()
        for element in root.iter()
        if local_name(element.tag) == "loc"
        and element.text
        and element.text.strip()
    })

    print(f"Toplam bağlantı: {len(locations)}")

    turkey_candidates = [
        url
        for url in locations
        if any(
            marker in url.casefold()
            for marker in ("/tr/", "-tr", "_tr", "turkey", "turkiye")
        )
    ]

    print("\nTÜRKİYE İÇİN OLASI BAĞLANTILAR")

    for url in turkey_candidates[:30]:
        print(url)

    if not turkey_candidates:
        print("URL isminden Türkiye bağlantısı belirlenemedi.")

    print("\nİLK 15 BAĞLANTI")

    for url in locations[:15]:
        print(url)


if __name__ == "__main__":
    main()