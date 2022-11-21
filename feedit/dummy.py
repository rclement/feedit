import logging

from concurrent import futures
from datetime import datetime, timezone
from urllib.parse import urljoin

from .common import PageEntry, PageIndex


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


base_url = "https://dummy.com"


def fetch_page_index() -> PageIndex:
    logger.info("fetching index page")

    return PageIndex(
        base_url=base_url,
        title="A dummy title",
        description="A dummy description",
        logo_url=urljoin(base_url, "favicon.ico"),
        language="en",
        urls=[urljoin(base_url, f"/news?page={i}") for i in range(3)],
    )


def fetch_page_entries(url: str) -> list[PageEntry]:
    logger.info(f"fetch page entries: {url}")

    return [
        PageEntry(
            link=url,
            date=datetime.now(tz=timezone.utc).isoformat(),
            title=f"Article Title {i}",
            summary=f"Article summary {i}",
        )
        for i in range(4)
    ]


def fetch(max_workers: int = 4) -> tuple[PageIndex, list[PageEntry]]:
    logger.info("fetch")

    page_index = fetch_page_index()

    logger.info(f"fetching {len(page_index.urls)} pages")
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        page_entries = [
            entry
            for entries in executor.map(fetch_page_entries, page_index.urls)
            for entry in entries
        ]
    logger.info(f"fetched {len(page_entries)} entries")

    return page_index, page_entries
