#!/usr/bin/env python3
from .unshuffle import get_word_id

import logging

logger = logging.getLogger(__name__)

class Dict:
    """Load dict and init variables."""

    def __init__(self, dict_: str):
        self._load_dict(dict_)

    def _load_dict(self, dict_):
        self.dictionary = {}

        def load_dict_from_file(dict_file):
            with open(dict_file, "r", encoding="utf-8") as df_handle:
                for line in df_handle:
                    add_to_dict(line)

        def load_dict_from_text(text):
            for line in text.split("\n"):
                add_to_dict(line)

        def add_to_dict(line):
            key, word, _ = line.split(" ")
            self.dictionary[key] = word.strip()

        if "\n" in dict_:
            load_dict_from_text(dict_)
        else:
            load_dict_from_file(dict_)
        logger.info("Dict loaded: %d entries", len(self.dictionary))


def generate(frequency_file, dict_file):
    """Generate dictionary file.

    Source file is expected to be in following format:
    `[number] [word] [frequency]`

    Default source files used are taken from
    (https://wortschatz.uni-leipzig.de/en/download/German#deu_news_2021)[Uni Leipzig Corpora]

    - Lines with multiple words or single characters are ignored
    - If more than 1 fingerprint/key exists for a word, the less frequent word will be ignored
    """
    dictionary = {}
    duplicates = 0
    ignored = 0
    lines = 0

    with open(frequency_file, "r", encoding="utf-8") as ff_handle:
        for line in ff_handle:
            lines += 1
            try:
                _, *word, frequency = line.split()

                if len(word) > 1:
                    # Ignore multiple words
                    word = " ".join(w for w in word)
                    raise ValueError("Sentence")

                word = word[0].strip()

                # Ignore single characters
                if len(word) == 1:
                    raise ValueError("Single")

                key = get_word_id(word)
                existing_entry = dictionary.get(key, None)

                # Skip if existing entry is more common
                if existing_entry is not None and int(existing_entry[1]) > int(
                    frequency
                ):
                    duplicates += 1
                    raise ValueError("Duplicate")

                dictionary[key] = [word, frequency]
            except ValueError as exc:
                logger.debug(
                    "Ignored line %s: '%s' (n=%d): %s",
                    lines,
                    word,
                    int(frequency),
                    str(exc),
                )
                ignored += 1

    logger.info("Lines checked: %s", lines)
    logger.info("Words ignored (thereof dupes): %d (%d) ", ignored, duplicates)

    with open(dict_file, "w", encoding="utf-8") as df_handle:
        for k, i in dictionary.items():
            df_handle.write(k + " " + i[0] + " " + i[1] + "\n")
    dict_len = len(dictionary.items())
    logger.info("Dictionary %s with %d entries generated from %s", dict_file, dict_len, frequency_file)
