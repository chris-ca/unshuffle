#!/usr/bin/env python3
import logging
import requests
import re
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose

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
    tag='p'
    for site in urlpatterns:
        if re.search(site, url):
            tag=urlpatterns[site][0]
            class_=urlpatterns[site][1]
            break 

    logger.debug("Looking for paragraphs matching class: "+class_)
    text = ''
    for p in soup.find_all(tag, class_=class_):
        text += p.text

    if text == '':
        raise TextNotFoundException("Shuffled text not found in response")

    return text

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
        try:
            text = Text(Dict(args.dict))
            text.shuffled = args.text if args.text is not None else get_text_from_url(args.url)
            logger.debug('Original: '+text.shuffled)
            print(text)
            transl_percent = round(text.translated / (text.not_translated + text.translated)*100,1)
            logger.info(f'Translated: {text.translated} ({transl_percent}%), unknown: {text.not_translated}')
        except TextNotFoundException as e:
            print(str(e))
    elif args.command == 'make_dict':
        generate_dict(args.src_file, args.dict)
    elif args.command == 'id':
        print(get_word_id(args.text))

