#!/usr/bin/env python3
import re
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_text_from_url(url, timeout=10) -> str:
    """GET Url and extract shuffled text from it.

    Different domains may use different HTML tags and classes.

    Params:
       url: URL to fetch
    Returns:
       text: Plain text of shuffled text
    """
    # example url: https://rp-online.de/nrw/staedte/krefeld/feuerwehr-in-krefeld-warum-ist-kohlenmonoxid-gefaehrlich_aid-81487981

    urlpatterns = {
        "saarbruecker-zeitung.de": ["p", "text-blurred"],
        "volksfreund.de": ["p", "text-blurred"],
        "ga.de": ["p", "text-blurred"],
        "rp-online.de": ["div", "blur-sm"],
    }

    headers = {"User-agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}

    response = requests.get(url, headers=headers, timeout=timeout)
    logger.info("Got response, size: %s", str(len(response.text)))

    soup = BeautifulSoup(response.text, "html.parser")

    class_ = "text-blurred"
    tag = "p"
    for site, selectors in urlpatterns.items():
        if re.search(site, url):
            tag = selectors[0]
            class_ = selectors[1]
            break

    logger.debug("Looking for paragraphs matching class: %s", class_)
    text = ""
    for p in soup.find_all(tag, class_=class_):
        text += p.text

    return text
