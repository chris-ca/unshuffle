#!/usr/bin/env python3
"""A module to "decrypt" shuffled words based on the frequency of occurance in everyday language.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""
import re

import logging

logger = logging.getLogger(__name__)

RX_PUNCTUATION = re.compile("[)('\"“„.,;:?!/-]")


class WordNotFound(Exception):
    """The (regular) word is not in the dictionary."""


class NotAWord(Exception):
    """The string is not a word, but rather a delimiter"""


class Untranslatable(Exception):
    """Raised if word cannot be"""


class Dict:
    """Load dict and init variables."""

    def __init__(self, dict_):
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


def generate_dict(frequency_file, dict_file):
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
    logger.info("Dictionary %s with %d entries generated ", dict_file, dict_len)


class Text:
    """Generate dictionary and 'translate' the actual text."""

    # If a string contains only non-alphanumeric characters it is considered
    # not a word
    RX_NONWORDS = re.compile(r"^[\s.,;:?!/-]+$")

    def __init__(self, dict_):
        """Load dict and init variables."""
        self.dictionary = dict_.dictionary
        self.tokens_processed = 0
        self.tokens_translated = 0
        self.tokens_not_translated = 0
        self.tokens_not_words = 0
        self._shuffled = None
        self._unshuffled = None

    def _is_a_word(self, token) -> bool:
        """Return True if string seems to be a word, otherwise False"""
        if len(token) == 1:
            return False
        if re.match(self.RX_NONWORDS, token):
            return False
        return True

    def __repr__(self):
        return self.unshuffled

    def translate_token(self, token: str) -> str:
        """Return translation of a string (token).

        If the token contains non-alphanumeric characters (e.g. punctuation)
        translation including those characters is tried.

        Args:
            token: the garbled string to translate
        Returns:
            token: the translated string
        Raises:
            WordNotFound: if a token is not in dictionary
            NotAWord: if string contains only whitespace or non-alnum characters
            Untranslatable: if string cannot be translated (e.g. multi digit numbers)
        """
        if not self._is_a_word(token):
            raise NotAWord

        if re.findall("[0-9]{2,}", token):
            raise Untranslatable

        punctuation = ""
        try:
            key = get_word_id(token)

            if key in self.dictionary:
                return self.dictionary[key]

            token, punctuation = word_parts(token)
            key = get_word_id(token)
            token = self.dictionary[key]
            return token + punctuation

        except (KeyError, ValueError) as exc:
            raise WordNotFound from exc

    @property
    def percent_translated(self):
        self.translate()
        return round(
            self.tokens_translated / (self.tokens_translated + self.tokens_not_translated) * 100, 1
        )

    @property
    def unshuffled(self):
        """return translated text"""
        if self._unshuffled is None:
            self._unshuffled = self.translate()
        return self._unshuffled

    @property
    def shuffled(self):
        """return shuffled text"""
        return self._shuffled

    @shuffled.setter
    def shuffled(self, text):
        """set shuffled text"""
        self._shuffled = text

    def translate(self) -> str:
        """Return translation of paragraph or word.

        Args:
            shuffled: the shuffled string to translate
        Returns:
            Text: Text object
        """
        block = ""

        for token in re.split(r"(\s+)", self.shuffled):
            self.tokens_processed += 1
            try:
                token = self.translate_token(token)
                self.tokens_translated += 1
            except WordNotFound:
                token = f"w¿{token}?"
                self.tokens_not_translated += 1
            except Untranslatable:
                token = f"u¿{token}?"
                self.tokens_not_translated += 1
            except NotAWord:
                self.tokens_not_words += 1
            block += token

        return block

def get_word_id(word: str) -> str:
    """Return string in alphabetical order."""
    return "".join(sorted(word))


def word_parts(word: str) -> list:
    """Separate punctuation and letters.

    Returns:
        - word, punctuation
    Throws:
        - KeyError if a word cannot be parsed
    """
    match = re.search(RX_PUNCTUATION, word)
    punctuation = ""
    if match is not None:
        punctuation = match[0]
        word = RX_PUNCTUATION.sub("", word)
    return word, punctuation
