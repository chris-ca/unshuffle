#!/usr/bin/env python4
"""Test translation"""
import pytest

from unshuffle.unshuffle import Text, word_id, WordNotFound, NotAWord, Untranslatable


@pytest.mark.parametrize(
    "word, key",
    [("und", "dnu"), ("der", "der"), ("erd", "der"), ("eis", "eis"), ("sie", "eis")],
)
def test_get_id(word, key):
    assert word_id(word) == key


@pytest.mark.parametrize(
    "shuffled, unshuffled, expected_translation",
    [
        ("Bnerkastel-Kseu", "Bernkastel-Kues", True),
        ("Wiehnenctah", "Weihnachten", True),
        ("teOsnr", "Ostern", True),
        ("INVALIDKEY", "INVALIDWORD", False),
    ],
)
def test_translate_token(text, unshuffled, shuffled, expected_translation):
    if expected_translation:
        assert unshuffled == text.translate_token(shuffled)
    else:
        with pytest.raises(WordNotFound):
            text.translate_token(shuffled)


@pytest.mark.parametrize(
    "token",
    [
        (",,,!"),
        ("  "),
        ("A"),
    ],
)
def test_raise_if_translate_nonwords(text, token):
    with pytest.raises(NotAWord):
        text.translate_token(token)


@pytest.mark.parametrize(
    "token",
    [
        ("348240"),
        ("12"),
        ("432849@39"),
    ],
)
def test_raise_if_untranslatable(text, token):
    with pytest.raises(Untranslatable):
        text.translate_token(token)


@pytest.mark.parametrize(
    "shuffled, unshuffled",
    [
        [
            "Orsten estht vro rde Trüe!\n\t\nWir fueren snu -- o?erd",
            "Ostern steht vor der Türe!\n\t\nWir freuen uns -- oder?",
        ]
    ],
)
def test_translate_paragraph(text, shuffled, unshuffled):
    assert isinstance(text, Text)
    text.shuffled = shuffled
    assert str(text) == unshuffled
