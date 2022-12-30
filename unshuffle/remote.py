#!/usr/bin/env python3
"""Extract shuffled text from websites.

Only very few websites are supported at the moment
"""
import re
import logging
import requests
from bs4 import BeautifulSoup

from .config import urlpatterns

logger = logging.getLogger(__name__)


class UrlNotSupportedException(Exception):
    pass


class TextNotFoundException(Exception):
    pass


def get_selectors(url) -> tuple:
    class_ = "text-blurred"
    tag = "p"
    for site, selectors in urlpatterns.items():
        if re.search(site, url):
            tag = selectors[0]
            class_ = selectors[1]
            break
    return tag, class_


def text_from_url(url):
    tag, class_ = get_selectors(url)
    response_body = get_url(url)
    return extract_text(response_body, class_=class_, tag=tag)


def get_url(url, timeout=10, headers=None) -> str:
    """GET URL and extract shuffled text from it.

    Different domains may use different HTML tags and classes.

    Params:
       url: URL to fetch
    Returns:
       text: Plain text of shuffled text
    """
    headers = {} if headers is None else headers
    if "User-agent" not in headers:
        headers = {"User-agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}

    response = requests.get(url, headers=headers, timeout=timeout)
    logger.info("Got response, size: %s", str(len(response.text)))
    logger.debug("Response: %s", response.text)
    return response.text


def extract_text(html, tag="p", class_="text-blurred") -> str:
    """Search for matching nodes in HTML.

    Return:
        text: the shuffled text
    """
    soup = BeautifulSoup(html, "html.parser")

    logger.debug("Looking for paragraphs matching class: %s", class_)
    text = ""
    for p in soup.find_all(tag, class_=class_):
        text += p.text

    if text == "":
        raise TextNotFoundException("Shuffled text not found in Response")

    return text
