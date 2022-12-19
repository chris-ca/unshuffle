## Idee
Einige Websites zeigen unregistrierten Nutzern nur Platzhalter-Text, bei dem die Buchstaben einzelner Wörter durcheinandergewürfelt sind.

Ziel des Programms ist es
- Die Textteile aus der Website zu extrahieren
- Anhand eines Wörterbuchs die einzelnen Wörter in "echte" Wörter zu übersetzen

## Entwicklungsziele
- `pylint` Hinweise weitestmöglich korrigieren
- `black` Formatregeln 
- `pytest` durchlaufend mit größtmöglicher Code Coverage

## Out of Scope / Bekannte Probleme
- Keine Kontexterkennung: Zeichenketten werden isoliert betrachtet und allein aufgrund der enthaltenen Zeichen erraten
- Zahlen können nicht erraten werden
- Kurze Zeichenketten (Sie, Sei, Eis) können häufig nicht zuverlässig übersetzt werden

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

