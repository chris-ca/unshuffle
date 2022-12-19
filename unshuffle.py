#!/usr/bin/env python3
"""A module to "decrypt" shuffled words based on the frequency of occurance in everyday language.
"""
import sys, re

import logging

logger = logging.getLogger(__name__)

RX_PUNCTUATION = re.compile('[)(\'"“„.,;:?!/-]')

class WordNotFound(Exception):
    """The (regular) word is not in the dictionary."""
    pass

class NotAWord(Exception):
    """The string is not a word, but rather a delimiter"""
    pass

class Untranslatable(Exception):
    """Raised if word cannot be """
    pass

class Dict():
    """Load dict and init variables."""

    def __init__(self, dict_):
        self._load_dict(dict_)

    def _load_dict(self, dict_):
        self.dictionary = {}

        def load_dict_from_file(dict_file):
            with open(dict_file, 'r') as df:
                for line in df:
                    add_to_dict(line)

        def load_dict_from_text(text):
            for line in text.split("\n"):
                add_to_dict(line)

        def add_to_dict(line):
            key, word, _ =  line.split(' ')
            self.dictionary[key] = word.strip()

        if "\n" in dict_:
            load_dict_from_text(dict_)
        else:
            load_dict_from_file(dict_)
        logger.info('Dict loaded: {} entries'.format(len(self.dictionary)))

def generate_dict(frequency_file, dict_file):
    """Generate dictionary file.

    Source file is expected to be in following format:
    `[number] [word] [frequency]`

    Default source files used are taken from (https://wortschatz.uni-leipzig.de/en/download/German#deu_news_2021)[Uni Leipzig Corpora]

    - Lines with multiple words or single characters are ignored
    - If more than 1 fingerprint/key exists for a word, the less frequent word will be ignored
    """
    dictionary = {}
    duplicates = 0
    ignored = 0
    lines = 0

    with open(frequency_file, 'r') as ff:
        for line in ff:
            lines += 1
            try:
                pos, *word, frequency =  line.split()

                if len(word) > 1:
                    """Ignore multiple words""" 
                    word = ' '.join(w for w in word)
                    raise ValueError("Sentence")

                word = word[0].strip()

                """Ignore single characters""" 
                if len(word) == 1:
                    raise ValueError("Single")

                key = get_word_id(word)
                existing_entry = dictionary.get(key, None)

                # Skip if existing entry is more common
                if existing_entry != None and int(existing_entry[1]) > int(frequency):
                    duplicates += 1
                    raise ValueError('Duplicate')

                dictionary[key] = [word, frequency]
            except ValueError as e:
                logger.debug(f"Ignored line {lines}: '{word}' (n={frequency}): "+str(e))
                ignored += 1

    logger.info(f"Lines checked: {lines}")
    logger.info(f"Words ignored (thereof dupes): {ignored} ({duplicates}) ")

    with open(dict_file, 'w') as df:
        for k, i in dictionary.items():
            df.write(k+" "+i[0]+" "+i[1]+"\n")
    dict_len = len(dictionary.items())
    logger.info(f"Dictionary {dict_file} with {dict_len} entries generated ")

class Text:
    """Generate dictionary and 'translate' the actual text."""

    """If a string contains only non-alphanumeric characters it is considered
    not a word"""
    RX_NONWORDS = re.compile(r'^[\s.,;:?!/-]+$')

    def __init__(self, dict_):
        """Load dict and init variables."""
        self.dictionary = dict_.dictionary
        self.token = 0
        self.translated = 0
        self.not_translated = 0
        self.non_words = 0
        self._shuffled = None

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

        if re.findall('[0-9]{2,}', token):
            raise Untranslatable

        punctuation = ''
        try:
            key = get_word_id(token)
            if key in self.dictionary:
                token = self.dictionary[key]
                return token
            else:
                token, punctuation = word_parts(token)
                key = get_word_id(token)
                token = self.dictionary[key]
                return token+punctuation
        except (KeyError, ValueError):
            raise WordNotFound

    @property
    def unshuffled(self):
        return self.translate()

    @property
    def shuffled(self):
        return self._shuffled

    @shuffled.setter
    def shuffled(self, s):
        self._shuffled = s

    def translate(self) -> str:
        """Return translation of paragraph or word.

        Args:
            shuffled: the shuffled string to translate
        Returns:
            Text: Text object
        """
        block = ''
        
        for token in re.split(r'(\s+)', self.shuffled):

            try:
                token = self.translate_token(token)
                self.translated += 1
            except WordNotFound:
                token = f"w¿{token}?"
                self.not_translated += 1
            except Untranslatable:
                token = f"u¿{token}?"
                self.not_translated += 1
            except NotAWord:
                self.non_words += 1
                pass
            block += token

        return block

def get_word_id(word: str) -> str:
    """Return string in alphabetical order."""
    return ''.join(sorted(word))

def word_parts(word: str) -> list:
    """Separate punctuation and letters.

    Returns:
        - word, punctuation
    Throws:
        - KeyError if a word cannot be parsed
    """
    match = re.search(RX_PUNCTUATION, word)
    punctuation = ''
    if match is not None:
        punctuation = match[0]
        word = RX_PUNCTUATION.sub('', word)
    return word, punctuation

