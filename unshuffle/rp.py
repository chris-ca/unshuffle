#!/usr/bin/env python3
"""Extract shuffled text from "Rheinische Post" websites.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python rp.py --url https://rp-online.de/nrw/panorama/wandern-in-nrw-sieben-spaziergaenge-fuer-die-feiertage_aid-81363323


Todo:
    * blah
    * bloph
"""
import logging
import requests
import re
from bs4 import BeautifulSoup

from unshuffle import Text, Dict, generate_dict, get_word_id

logger = logging.getLogger(__name__)


class TextNotFoundException(Exception):
    pass


def get_text_from_url(url) -> str:
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

    response = requests.get(url, headers=headers)
    logger.info("Got response, size: " + str(len(response.text)))

    soup = BeautifulSoup(response.text, "html.parser")

    class_ = "text-blurred"
    tag = "p"
    for site in urlpatterns:
        if re.search(site, url):
            tag = urlpatterns[site][0]
            class_ = urlpatterns[site][1]
            break

    logger.debug("Looking for paragraphs matching class: " + class_)
    text = ""
    for p in soup.find_all(tag, class_=class_):
        text += p.text

    if text == "":
        logger.debug(response.text)
        raise TextNotFoundException("Shuffled text not found in response")

    return text


if __name__ == "__main__":
    import argparse
    import requests_cache

    requests_cache.install_cache("demo_cache")

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["translate", "make_dict", "id"])
    parser.add_argument("--text", default=None, type=str, help="Text to translate")
    parser.add_argument("--url", type=str, help="URL to get text from")
    parser.add_argument(
        "--dict", type=str, default="data/dict.txt", help="Dictionary file to use"
    )
    parser.add_argument(
        "--src-file",
        type=str,
        default="data/frequency.txt",
        help="Frequency file to use as base for dictionary",
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    args = parser.parse_args()

    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(module)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(args.loglevel)

    if args.command == "translate":
        try:
            text = Text(Dict(args.dict))
            text.shuffled = (
                args.text if args.text is not None else get_text_from_url(args.url)
            )
            text.translate()
            logger.info(
                "Stats: %d words translated (%d%%), %d words unknown",
                text.tokens_translated,
                text.percent_translated,
                text.tokens_not_translated,
            )
        except TextNotFoundException as e:
            print(str(e))
    elif args.command == "make_dict":
        generate_dict(args.src_file, args.dict)
    elif args.command == "id":
        print(get_word_id(args.text))
