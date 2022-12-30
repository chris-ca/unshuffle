#!/usr/bin/env python3
'''Generate dicts
in everyday language.

There is no further analysis of the grammar or meaning of the word. Shuffled
strings are simply replaced based on the generated dictionary.

Generate and use Dict like this::

    generate('frequency.txt', 'dict.txt')
    d = Dict('dict.txt')

'''
import logging

from .unshuffle import word_id

logger = logging.getLogger(__name__)


class Dict:
    '''Load dict and init variables.'''

    def __init__(self, dict_: str):
        self._load_dict(dict_)

    def __contains__(self, s):
        return s in self.dictionary

    def _load_dict(self, dict_):
        self.dictionary = {}

        def load_dict_from_file(dict_file):
            with open(dict_file, 'r', encoding='utf-8') as df_handle:
                for line in df_handle:
                    add_to_dict(line)

        def load_dict_from_text(text):
            for line in text.split('\n'):
                add_to_dict(line)

        def add_to_dict(line):
            key, word, _ = line.split(' ')
            self.dictionary[key] = word.strip()

        if '\n' in dict_:
            load_dict_from_text(dict_)
        else:
            load_dict_from_file(dict_)
        logger.info('Dict loaded: %d entries', len(self.dictionary))


class DictionaryConverter:
    @staticmethod
    def from_type(type_, kwargs):
        cls = (type_.title()+'DictConverter')
        cls = globals()[cls]
        return cls(**kwargs)

    def __contains__(self, s):
        return s in self.dictionary


class FrequencyDictConverter(DictionaryConverter):
    '''Convert frequency file to dict.'''
    def __init__(self, frequency_file: str, dict_file: str):
        self.frequency_file = frequency_file
        self.dict_file = dict_file
        self.dictionary = {}
        self.duplicates = 0
        self.ignored = 0
        self.lines = 0

    @staticmethod
    def parse_line(line: str) -> tuple:
        '''Get word+frequency from line.'''
        _, *word, frequency = line.split()

        # Ignore multiple words
        if len(word) > 1:
            word = ' '.join(w for w in word)
            raise ValueError('Sentence')

        word = word[0].strip()

        # Ignore single characters
        if len(word) == 1:
            raise ValueError('Single')

        return word, frequency

    def raise_if_entry_exists(self, key, frequency):
        existing_entry = self.dictionary.get(key, None)
        # Skip if an existing entry is more common
        if existing_entry and int(existing_entry[1]) > int(frequency):
            self.duplicates += 1
            raise ValueError('Duplicate')

    def generate(self):
        '''Generate dictionary file.

        Source file is expected to be in following format:
        `[number] [word] [frequency]`

        Default source files used are taken from
        (https://wortschatz.uni-leipzig.de/en/download/German#deu_news_2021)[Uni Leipzig Corpora]

        - Lines with multiple words or single characters are ignored
        - If more than 1 fingerprint/key exists for a word, the less frequent word will be ignored
        '''

        with open(self.frequency_file, 'r', encoding='utf-8') as ff_handle:
            for line in ff_handle:
                self.lines += 1
                try:
                    word, frequency = self.parse_line(line)
                    key = word_id(word)
                    self.raise_if_entry_exists(key, frequency)
                    self.dictionary[key] = [word, frequency]
                except ValueError as exc:
                    logger.debug(
                        'Ignored line %s: "%s" (n=%d): %s',
                        self.lines,
                        word,
                        int(frequency),
                        str(exc),
                    )
                    self.ignored += 1

        logger.info('Lines checked: %s', self.lines)
        logger.info(
            'Words ignored (thereof dupes): %d (%d) ', self.ignored, self.duplicates
        )

        self.save()

    def save(self):
        with open(self.dict_file, 'w', encoding='utf-8') as df_handle:
            for k, i in self.dictionary.items():
                df_handle.write(k + ' ' + i[0] + ' ' + i[1] + '\n')
        dict_len = len(self.dictionary.items())
        logger.info(
            'Dictionary %s with %d entries generated from %s',
            self.dict_file,
            dict_len,
            self.frequency_file,
        )
