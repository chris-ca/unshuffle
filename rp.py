#!/usr/bin/env python3
import sys, re
import requests
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose

import logging

logger = logging.getLogger(__name__)
RX_PUNCTUATION = re.compile('[)(\'"“„.,;:?!/-]')


class WordNotFound(Exception):
    pass

class NonWordString(Exception):
    pass

class Untranslatable(Exception):
    pass

class Translator:

    """
    If a string contains only non-alphanumeric characters it is considered
    not a word
    """
    RX_NONWORDS = re.compile(r'^[\s.,;:?!/-]+$')

    def __init__(self, dict_):
        self.load_dict(dict_)
        self.token = 0
        self.translated = 0
        self.not_translated = 0
        self.non_words = 0

    def load_dict(self, dict_):
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

    def is_nonword(self, token) -> bool:
        if len(token) == 1:
            return True
        return re.match(self.RX_NONWORDS, token)

    def translate_token(self, token: str) -> str:
        """ Return translation of a string

        Args:
            word: the garbled string to translate

        Returns:
            word: the translated word string to translate

        Raises:
            WordNotFound: if a regular word is not in dictionary
            NonWordString: if string contains only whitespace or non-alnum characters
            Untranslatable: if string cannot be translated (e.g. multi digit numbers)
        
        """

        if self.is_nonword(token):
            raise NonWordString

        if re.findall('[0-9]{2,}', token):
            raise Untranslatable

        punctuation = ''
        try:
            token, punctuation = word_parts(token)
            key = get_word_id(token)
            token = self.dictionary[key]
        except (KeyError, ValueError):
            raise WordNotFound

        return token+punctuation

    def translate(self, text: str) -> str:
        """ Return translation of paragraph or word

        Args:
            text: the garbled string to translate

        Returns:
            text: the translated text. Unknown words will be surrounded with '?'
        """
        
        block = ''
        
        for token in re.split(r'(\s+)', text):

            try:
                token = self.translate_token(token)
                self.translated += 1
            except WordNotFound:
                token = f"w¿{token}?"
                self.not_translated += 1
            except Untranslatable:
                token = f"u¿{token}?"
                self.not_translated += 1
            except NonWordString:
                self.non_words += 1
                pass
            block += token
        #breakpoint()
        
        return block

def get_text_from_url(url) -> str:
    """ Different sites may use different classes """
    # example url: https://rp-online.de/nrw/staedte/krefeld/feuerwehr-in-krefeld-warum-ist-kohlenmonoxid-gefaehrlich_aid-81487981

    urlpatterns = {
        'saarbruecker-zeitung.de'   : ['p', 'text-blurred'],
        'volksfreund.de'            : ['p', 'text-blurred'],
        'ga.de'                     : ['p', 'text-blurred'],
        'rp-online.de'              : ['div', 'blur-sm']
    }

    headers = {'User-agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}

    response = requests.get(url, headers=headers)
    logger.info('Got response, size: '+ str(len(response.text)))

    soup = BeautifulSoup(response.text, 'html.parser')

    class_='text-blurred'
    for site in urlpatterns:
        if re.search(site, url):
            tag=urlpatterns[site][0]
            class_=urlpatterns[site][1]
            break 

    logger.debug("Looking for paragraphs matching class: "+class_)
    text = ''
    for p in soup.find_all(tag, class_=class_):
        text += p.text
    return text


def get_word_id(word: str) -> str:
    """ return string in alphabetical order """
    return ''.join(sorted(word))

def word_parts(word: str) -> list:
    """ separate punctuation and letters

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

def generate_dict(frequency_file, dict_file):
    """ Generate dictionary file

    Source is expecting a file in the format

    `[number] [word] [frequency]`

    Files used are taken from (https://wortschatz.uni-leipzig.de/en/download/German#deu_news_2021)[Uni Leipzig Corpora]

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
                    """ Ignore multiple words """ 
                    word = ' '.join(w for w in word)
                    raise ValueError("Sentence")

                word = word[0].strip()

                """ Ignore single characters """ 
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
    logger.info(f"Words ignored(dupes): {ignored}/({duplicates}) ")

    with open(dict_file, 'w') as df:
        for k, i in dictionary.items():
            df.write(k+" "+i[0]+" "+i[1]+"\n")

if __name__ == '__main__':
    import argparse
    import requests_cache
    requests_cache.install_cache('demo_cache')

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=['translate','make_dict', 'id'])
    parser.add_argument("--text", default=None, type=str, help="Text to translate")
    parser.add_argument("--url", type=str, help="URL to get text from")
    parser.add_argument("--dict", type=str, default='data/dict.txt', help="Dictionary file to use")
    parser.add_argument("--src-file", type=str, default='data/frequency.txt', help="Frequency file to use as base for dictionary")
    parser.add_argument("--debug", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.setLevel(args.loglevel)

    if args.command == 'translate':
        d = Translator(args.dict)
        text = args.text if args.text is not None else get_text_from_url(args.url)
        logger.debug('Original: '+text)
        print(d.translate(text))
        transl_percent = round(d.translated / (d.not_translated + d.translated)*100,1)
        logger.info(f'Translated: {d.translated} ({transl_percent}%) , unknown: {d.not_translated}, skipped: {d.non_words}')

    elif args.command == 'make_dict':
        generate_dict(args.src_file, args.dict)
    elif args.command == 'id':
        print(get_word_id(args.text))
