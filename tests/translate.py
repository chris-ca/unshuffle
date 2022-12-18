#!/usr/bin/env python4
import pytest
import random

from unshuffle import *

@pytest.fixture

def shuffle_word(word):
    return ''.join(random.sample(word, len(word)))

@pytest.fixture
def shuffled_text(original_text):
    shuffled = []
    for word in original_text.split(' '):
        shuffled.append(shuffle_word(word))
    return ' '.join(shuffled) 

@pytest.mark.parametrize(
    "word, key",
    [
        ('und','dnu'),
        ('der','der'),
        ('erd','der'),
        ('eis','eis'),
        ('sie','eis')
    ],
)
def test_get_id(word, key):
    assert get_word_id(word) == key

def test_read_dictionary_from_text(dict_contents):
    t = Translator(dict_contents)
    assert type(t.dictionary) == dict

def test_read_dictionary_from_file(dict_file):
    t = Translator(dict_file)
    assert type(t.dictionary) == dict

@pytest.mark.parametrize(
    "shuffled, original, expected_translation",
    [
        ('Wiehnenctah','Weihnachten', True),
        ('teOsnr','Ostern', True),
        ('INVALIDKEY','INVALIDWORD', False)
    ],
)
def test_translate_token(translator, original, shuffled, expected_translation):
    if expected_translation:
        assert original == translator.translate_token(shuffled)
    else:
        with pytest.raises(WordNotFound):
            translator.translate_token(shuffled)

@pytest.mark.parametrize(
    "token",
    [
        (',,,!'),
        ('  '),
    ],
)
def test_translate_nonwords(translator, token):
    with pytest.raises(NotAWord):
        translator.translate_token(token)

@pytest.mark.parametrize(
    "shuffled, original",
    [
        ['Orsten estht vro rde Trüe!\n\t\nWir fueren snu -- o?erd', 'Ostern steht vor der Türe!\n\t\nWir freuen uns -- oder?']
    ]
)
def test_translate_paragraph(translator, shuffled, original):
    assert original == translator.translate(shuffled)
