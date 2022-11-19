from dataclasses import dataclass


@dataclass
class PageIndex:
    base_url: str
    title: str
    description: str
    logo_url: str
    language: str
    urls: list[str]


@dataclass
class PageEntry:
    link: str
    date: str
    title: str
    summary: str
