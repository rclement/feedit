import pytest

from feedit import urssaf_autoentrepreneur


@pytest.mark.vcr
def test_fetch_success() -> None:
    page_index, page_entries = urssaf_autoentrepreneur.fetch(max_workers=1)

    assert page_index.base_url
    assert page_index.title
    assert page_index.description
    assert page_index.logo_url
    assert page_index.language
    assert len(page_index.urls) > 0

    for entry in page_entries:
        assert entry.link
        assert entry.date
        assert entry.title
        assert entry.summary
