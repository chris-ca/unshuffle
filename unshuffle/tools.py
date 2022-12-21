#!/usr/bin/env python3
#####################################################################################################################
# Script Name     : .py 
# Description     : 
# 
# 
# 
# Requires        : 
# Arguments       :  
# Run Information : This script is run manually|via crontab.
# Author          : Chris, 2020
# Output          : 
#####################################################################################################################
import requests
import re
import logging
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

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
        "saarbruecker-zeitung.de": ["p", "text-blurred"],
        "volksfreund.de": ["p", "text-blurred"],
        "ga.de": ["p", "text-blurred"],
        "rp-online.de": ["div", "blur-sm"],
    }

    headers = {"User-agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}

    response = requests.get(url, headers=headers)
    logger.info("Got response, size: " + str(len(response.text)))

    soup = BeautifulSoup(response.text, "html.parser")

    class_ = "text-blurred"
    tag = "p"
    for site in urlpatterns:
        if re.search(site, url):
            tag = urlpatterns[site][0]
            class_ = urlpatterns[site][1]
            break

    logger.debug("Looking for paragraphs matching class: " + class_)
    text = ""
    for p in soup.find_all(tag, class_=class_):
        text += p.text

    return text
