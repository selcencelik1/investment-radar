import json

import inspect_kpmg_archive


def test_saves_archive_summary(tmp_path, monkeypatch):
    # Çıktıyı gerçek proje yerine pytest'in geçici klasörüne yönlendir.
    monkeypatch.setattr(
        inspect_kpmg_archive,
        name="__file__",
        value=str(tmp_path / "inspect_kpmg_archive.py"),
    )

    results = [
        {
            "url": "https://example.com/report-2024",
            "status": "READY",
            "period": "2024-FY",
            "count": 331,
            "detail": "",
        },
        {
            "url": "https://example.com/report-2023",
            "status": "NEEDS_REVIEW",
            "period": None,
            "count": None,
            "detail": "Rapor dönemi belirlenemedi.",
        },
    ]

    output_path = inspect_kpmg_archive.save_archive_summary(results)

    assert output_path == tmp_path / "data" / "archive_summary.json"
    assert output_path.exists()

    content = json.loads(output_path.read_text(encoding="utf-8"))

    assert content["total"] == 2
    assert content["ready"] == 1
    assert content["needs_review"] == 1
    assert content["reports"] == results
    assert content["completed_at"]
    assert not output_path.with_suffix(".json.tmp").exists()