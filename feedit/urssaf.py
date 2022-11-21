import logging
import dateparser
import requests

from concurrent import futures
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .common import PageEntry, PageIndex


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


base_url = "https://www.urssaf.fr/portail/home/actualites/toute-lactualite.html"


def cleanup_text(text: str) -> str:
    return text.replace("\xa0", " ")


def cleanup_date(text: str) -> str:
    text = cleanup_text(text)
    clean_date = dateparser.parse(
        text,
        date_formats=["%d %B %Y"],
        settings={"TIMEZONE": "Europe/Paris", "RETURN_AS_TIMEZONE_AWARE": True},
    )
    return clean_date.isoformat() if clean_date else text


def fetch_page_index() -> PageIndex:
    logger.info("fetching index page")

    rv = requests.get(base_url)
    body = rv.content.decode("utf-8")
    soup = BeautifulSoup(body, features="html.parser")

    title = el.get_text() if (el := soup.select_one("head > title")) else "urssaf.fr"
    description = el.get_text() if (el := soup.select_one("h1")) else title
    logo_url = (
        urljoin(base_url, str(el.get("href", "")))
        if (el := soup.select_one('head > link[rel="icon"]'))
        else ""
    )
    language = str(soup.get("lang", "fr"))
    urls = [base_url] + [
        urljoin(base_url, str(el.get("href", "")))
        for el in soup.select(".pagination .paginationPageUrl .pagerLink")
    ]

    return PageIndex(
        base_url=base_url,
        title=title,
        description=description,
        logo_url=logo_url,
        language=language,
        urls=urls,
    )


def fetch_page_entries(url: str) -> list[PageEntry]:
    logger.info(f"fetch page entries: {url}")

    rv = requests.get(url)
    body = rv.content.decode("utf-8")
    soup = BeautifulSoup(body, "html.parser")

    return [
        PageEntry(
            title=title,
            date=(
                cleanup_date(el.get_text())
                if (el := entry.select_one(".actualiteDate"))
                else ""
            ),
            summary=(
                cleanup_text(el.get_text())
                if (el := entry.select_one(".BlockActu > p:nth-child(2)"))
                else ""
            ),
            link=(
                urljoin(base_url, str(el.get("href")))
                if (el := entry.select_one(".BlockActu > a"))
                else ""
            ),
        )
        for entry in soup.select(".actualiteResume")
        if (
            title := (
                cleanup_text(el.get_text())
                if (el := entry.select_one(".BlockActu > .h2-like"))
                else None
            )
        )
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
