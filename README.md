## Idee

## Installation
- Requirements installieren
    ```bash
    pip install -r requirements.txt 
    ```
- Wortschatz Datei herunterladen
    ```bash
    wget https://downloads.wortschatz-leipzig.de/corpora/deu_news_2021_300K.tar.gz
    tar xf ~/Downloads/deu_news_2021_300K.tar.gz deu_news_2021_300K/deu_news_2021_300K-words.txt
    ```
- "Dictionary" generieren
    ```bash
    $ ./rp.py make_dict --src-file deu_news_2021_300K/deu_news_2021_300K-words.txt --dict dict.txt
    INFO - Lines checked: 337606
    INFO - Words ignored(dupes): 39761/(9561)

    ```
