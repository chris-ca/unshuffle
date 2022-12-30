"""Test remote module"""
import pytest

from unshuffle.remote import extract_text, get_selectors, \
    text_from_url, get_url, TextNotFoundException
import requests


@pytest.mark.parametrize(
    "file, tag, class_",
    [("rp.html", "div", "blur-sm"), ("ga.html", "p", "text-blurred")],
)
def test_extract_text(file, tag, class_):
    with open("tests/fixtures/" + file, "r", encoding="UTF-8") as fp:
        html = fp.read()
    assert extract_text(html, tag, class_) > ""


@pytest.mark.parametrize(
    "html",
    [
        ('<html><p class="">test text is not found</p></html>'),
        ('<html><div class="text-blue">test text is not found</p></html>'),
    ],
)
def test_fail_if_text_not_found(html):
    with pytest.raises(TextNotFoundException):
        extract_text(html)


@pytest.mark.parametrize("url, tag, class_", [("https://ga.de/", "p", "text-blurred")])
def test_get_selectors(url, tag, class_):
    r_tag, r_class_ = get_selectors(url)
    assert r_tag == tag
    assert r_class_ == class_


@pytest.mark.parametrize(
    "url",
    [
        ("https://HOST-NOT-EXISTING"),
        ("https://invalid\\url"),
    ],
)
def test_fail_if_invalid_url(url):
    with pytest.raises(requests.exceptions.ConnectionError):
        get_url(url)


@pytest.mark.parametrize(
    "url",
    [
        ("https://ga.de/region/sieg-und-rhein/troisdorf/"
            "s13-troisdorf-bleibt-auf-unbestimmte-zeit-endstation_aid-82139435")
    ],
)
def test_get_text_from_url(url):
    text = text_from_url(url)
    assert len(text) > 100
