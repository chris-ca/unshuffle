#!/usr/bin/env python3
"""A module to 'decrypt' shuffled words based on the frequency of occurance
in everyday language.

There is no further analysis of the grammar or meaning of the word. Shuffled
strings are simply replaced based on the generated dictionary.

Example::

    shuffled_text = 'grubereheCes'
    txt = Text(Dict('dict.txt'))
    txt.shuffled = shuffled_text
    # Prints: Cheeseburger
    print(txt)
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
        if len(token) <= 1:
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
            # try including punctuation
            key = word_id(token)

            if key in self.dictionary:
                return self.dictionary[key]

            # try again without punctuation
            token, punctuation = word_parts(token)
            key = word_id(token)
            token = self.dictionary[key]
            return token + punctuation

        except (KeyError, ValueError) as exc:
            raise WordNotFound from exc

    @property
    def percent_translated(self) -> int:
        """Return percentage of translated words or zero, if nothing was translated."""
        self.translate()
        total = self.tokens_translated + self.tokens_not_translated
        return (
            0
            if total == 0
            else round(
                self.tokens_translated / total * 100,
                1,
            )
        )

    @property
    def unshuffled(self) -> str:
        """return translated text"""
        if self._unshuffled is None:
            self._unshuffled = self.translate()
        return self._unshuffled

    @property
    def shuffled(self) -> str:
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


def word_id(word: str) -> str:
    """Return the unique id for the word."""

    # For now we're just sorting each string in alphabetical order
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
