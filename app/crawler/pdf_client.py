import time

import requests


def download_pdf(url: str) -> bytes:
    print(f"PDF is downloading: {url}", flush=True)

    chunks = []
    downloaded_bytes = 0
    last_report_time = time.monotonic()
    started_at = last_report_time

    with requests.get(
        url,
        stream=True,
        timeout=(10, 20),
    ) as response:
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue

            downloaded_bytes += len(chunk)
            chunks.append(chunk)

            now = time.monotonic()

            if now - last_report_time >= 2:
                print(
                    f"Downloaded: {downloaded_bytes / 1024 / 1024:.2f} MB",
                    flush=True,
                )
                last_report_time = now

            if downloaded_bytes > 50 * 1024 * 1024:
                raise ValueError("PDF, exceeded the 50 MB download limit.")

            if now - started_at > 120:
                raise TimeoutError("PDF exceeded the time limit.")

    pdf_bytes = b"".join(chunks)

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Downloaded content is not PDF.")

    print(
        f"PDF downloaded: {len(pdf_bytes) / 1024 / 1024:.2f} MB",
        flush=True,
    )

    return pdf_bytes