#!/usr/bin/env python3
import logging
import argparse
import requests_cache

from unshuffle.unshuffle import Text, get_word_id
from unshuffle.dict_ import Dict, generate
from unshuffle.tools import get_text_from_url

logger = logging.getLogger(__name__)


def run():
    """executed from command line"""
    requests_cache.install_cache("~/.cache/unshuffle.sqlite")
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
        text = Text(Dict(args.dict))
        text.shuffled = (
            args.text if args.text is not None else get_text_from_url(args.url)
        )

        if text.unshuffled == "":
            print("Text not found")
        else:
            print(text.unshuffled)

        logger.info(
            "Stats: %d words translated (%d%%), %d words unknown",
            text.tokens_translated,
            text.percent_translated,
            text.tokens_not_translated,
        )
    elif args.command == "make_dict":
        generate(args.src_file, args.dict)
    elif args.command == "id":
        print(get_word_id(args.text))


if __name__ == "__main__":
    run()
