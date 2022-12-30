[![Python application](https://github.com/chris-ca/unshuffle/actions/workflows/python-app.yml/badge.svg)](https://github.com/chris-ca/unshuffle/actions/workflows/python-app.yml)

## Idea
Some (German) news websites show placeholder texts to unregistered users. The placeholder text is generated from the actual article by shuffling the letters of individual words.

The goal of this package is 
- To extract the scrambled passage from the website
- To translate the shuffled words back to their original meaning


## Development goals
- *This is first and foremost an exercise project to improve my Python workflows and coding style*. 
- Use `pylint` to adhere to strict coding standards
- Use `black` for improved formatting
- Have `pytest` complete with high code coverage
- Have a package that can be installed using typical tools like `pip` or `poetry`

## Out of Scope / non-goals
- No contect recognition: words/tokens are being looked at individually and will be guessed only based on their containing characters and nothing else 
- By nature, numbers cannot be guessed
- Names or words containing the same letters will not be guessed correctly

## Installation
- Install with `poetry add unshuffle`
- Download initial word file (German):
    ```bash
    wget https://downloads.wortschatz-leipzig.de/corpora/deu_news_2021_300K.tar.gz
    tar xf ~/Downloads/deu_news_2021_300K.tar.gz deu_news_2021_300K/deu_news_2021_300K-words.txt
    ```
- Generate dictionary
    ```bash
    $ ./rp.py make_dict --src-file deu_news_2021_300K/deu_news_2021_300K-words.txt --dict dict.txt
    INFO - Lines checked: 337606
    INFO - Words ignored(dupes): 39761/(9561)
