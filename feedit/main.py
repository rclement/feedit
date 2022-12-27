import argparse
import importlib
import logging

from operator import attrgetter
from pathlib import Path
from feedgen.feed import FeedGenerator

from . import urssaf, urssaf_autoentrepreneur
from .common import PageEntry, PageIndex


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def generate_feed(index: PageIndex, entries: list[PageEntry]) -> FeedGenerator:
    sorted_entries = sorted(entries, key=attrgetter("date", "title"))
    latest_entry = sorted_entries[-1]

    feed = FeedGenerator()
    feed.id(index.base_url)
    feed.title(index.title)
    feed.updated(latest_entry.date)
    feed.lastBuildDate(latest_entry.date)
    feed.link(href=index.base_url, rel="self")
    feed.description(index.description)
    feed.logo(index.logo_url)
    feed.language(index.language)

    for entry in sorted_entries:
        feed_entry = feed.add_entry()
        feed_entry.id(entry.link)
        feed_entry.published(entry.date)
        feed_entry.updated(entry.date)
        feed_entry.title(entry.title)
        feed_entry.description(entry.summary)
        feed_entry.content(entry.summary)
        feed_entry.link(dict(href=entry.link))

    return feed


def save_feed(feed: FeedGenerator, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    feed.rss_file(output / "feed.rss")
    feed.atom_file(output / "feed.atom")


def command_fetch(args: argparse.Namespace) -> None:
    default_sources = [urssaf.__name__, urssaf_autoentrepreneur.__name__]
    sources = args.sources or default_sources
    for source in sources:
        source_mod = importlib.import_module(source)
        feed_index, feed_entries = source_mod.fetch(max_workers=args.max_workers)
        feed = generate_feed(feed_index, feed_entries)
        filename = args.output / source.split(".")[-1]
        save_feed(feed, filename)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Commands", required=True, dest="commands")

    parser_fetch = subparsers.add_parser("fetch", help="Fetch feeds from sources")
    parser_fetch.add_argument(
        "--sources",
        "-s",
        help="Specify which sources to fetch (default is all except `feedit.dummy`)",
        action="extend",
        nargs="+",
        type=str,
    )
    parser_fetch.add_argument(
        "--output", "-o", help="Output directory", type=Path, required=True
    )
    parser_fetch.add_argument(
        "--max-workers",
        "-w",
        help="Maximum workers to use for concurrent fetching",
        required=False,
        default="4",
        type=int,
    )
    parser_fetch.set_defaults(func=command_fetch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
