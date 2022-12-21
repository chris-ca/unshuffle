#!/usr/bin/env python3

from unshuffle.dict_ import Dict

def test_read_dictionary_from_text(dict_contents):
    t = Dict(dict_contents)
    assert type(t.dictionary) == dict

def test_read_dictionary_from_file(dict_file):
    t = Dict(dict_file)
    assert type(t.dictionary) == dict

