import requests


url = (
    "https://author.kpmg.com/content/dam/kpmg/tr/pdf/"
    "2023/05/turkish-startup-investments-2022.pdf"
)

try:
    with requests.get(
        url,
        timeout=30,
        stream=True,
        allow_redirects=False,
    ) as response:
        print(f"HTTP durumu: {response.status_code}")
        print(
            "İçerik türü:",
            response.headers.get("Content-Type", "Belirtilmemiş"),
        )
        print(
            "Yönlendirme:",
            response.headers.get("Location", "Yok"),
        )

        if response.status_code == 200:
            first_chunk = next(
                response.iter_content(chunk_size=1024),
                b"",
            )

            print(
                "PDF başlangıcı bulundu mu?:",
                first_chunk.startswith(b"%PDF-"),
            )

except requests.RequestException as error:
    print(f"Erişim hatası: {type(error).__name__}: {error}")