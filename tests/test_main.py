import pytest

from pathlib import Path

from feedit import main


@pytest.mark.vcr
def test_fetch_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "feedit.main",
            "fetch",
            "--output",
            str(tmp_path),
            "--max-workers",
            "1",
        ],
    )

    main.main()

    suffixes = [".rss", ".atom"]
    feeds = list(tmp_path.glob("**/*"))
    assert len(feeds) > 0
    for feed in feeds:
        if feed.is_file():
            assert feed.suffix in suffixes
