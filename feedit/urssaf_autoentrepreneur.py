import logging
import dateparser
import requests

from concurrent import futures
from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from bs4 import BeautifulSoup

from .common import PageEntry, PageIndex


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


base_url = "https://www.autoentrepreneur.urssaf.fr/portail/accueil/sinformer-sur-le-statut/toutes-les-actualites.html"


@dataclass
class Pagination:
    begin: tuple[str, int]
    end: tuple[str, int]
    pagesize: tuple[str, int]


def makeurl(url: str) -> str:
    return urljoin(base_url, url)


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


def fetch_page_entries(url: str) -> list[PageEntry]:
    logger.info(f"fetch page entries: {url}")

    rv = requests.get(url, timeout=30)
    body = rv.content.decode("utf-8")
    soup = BeautifulSoup(body, "html.parser")

    return [
        PageEntry(
            title=(
                cleanup_text(el.get_text())
                if (el := entry.select_one(".bloc_actu_item h3"))
                else ""
            ),
            date=(
                cleanup_date(el.get_text())
                if (el := entry.select_one(".bloc_actu_item .date"))
                else ""
            ),
            summary=(
                cleanup_text(el.get_text())
                if (el := entry.select_one(".introduction"))
                else ""
            ),
            link=(
                makeurl(str(el.get("href")))
                if (el := entry.select_one(".lien > .bloc_actu_lien"))
                else ""
            ),
        )
        for entry in soup.select(".bloc_actu")
    ]


def fetch_page_index() -> PageIndex:
    logger.info("fetching index page")

    rv = requests.get(base_url, timeout=30)
    body = rv.content.decode("utf-8")
    soup = BeautifulSoup(body, features="html.parser")

    last_page = (
        el.get("href")
        if (el := soup.select_one("li.page-item:last-of-type > a.page-link"))
        else ""
    )
    last_page_url = urlparse(str(last_page))
    last_page_qs = parse_qs(last_page_url.query)

    pagination = Pagination(begin=("", 0), end=("", 0), pagesize=("", 0))
    for k, v in last_page_qs.items():
        if k.startswith("begin"):
            pagination.begin = k, int(v[0])
        elif k.startswith("end"):
            pagination.end = k, int(v[0])
        elif k.startswith("pagesize"):
            pagination.pagesize = k, int(v[0])
        else:  # pragma: no cover
            pass

    num_pages = int(pagination.end[1] / pagination.pagesize[1])

    urls = [
        urljoin(
            base_url,
            "?"
            + urlencode(
                {
                    pagination.begin[0]: i * pagination.pagesize[1],
                    pagination.end[0]: ((i + 1) * pagination.pagesize[1]) - 1,
                    pagination.pagesize[0]: pagination.pagesize[1],
                }
            ),
        )
        for i in range(num_pages)
    ]

    title = (
        el.get_text()
        if (el := soup.select_one("head title"))
        else "autoentrepreneur.urssaf.fr"
    )
    description = (
        str(el.get("content", ""))
        if (el := soup.select_one('head meta[name="description"]'))
        else title
    )
    logo_url = (
        makeurl(str(el.get("href", "")))
        if (el := soup.select_one('head link[rel="icon"]'))
        else ""
    )

    return PageIndex(
        base_url=base_url,
        title=title,
        description=description,
        logo_url=logo_url,
        language=str(soup.get("lang", "fr")),
        urls=urls,
    )


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
