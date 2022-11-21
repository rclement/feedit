import pytest

from pathlib import Path

from feedit import main


@pytest.mark.block_network
def test_fetch_dummy_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "feedit.main",
            "fetch",
            "--sources",
            "feedit.dummy",
            "--output",
            str(tmp_path),
            "--max-workers",
            "1",
        ],
    )

    main.main()

    suffixes = [".rss", ".atom"]
    for suffix in suffixes:
        feed_path = (tmp_path / "dummy" / "feed").with_suffix(suffix)
        assert feed_path.exists()
        assert feed_path.is_file()
