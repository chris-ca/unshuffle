#!/usr/bin/env python3
import pytest

from rp import Dictionary

def test_read_dictionary_from_text(dict_contents):
    dict_ = Dictionary.read(dict_contents)
    assert type(dict_) == dict
    assert 'der' == dict_['der']
    assert 'von' == dict_['nov']
    assert 'hallo' == dict_['ahllo']

def test_read_dictionary_from_file(dict_file):
    dict_ = Dictionary.read(dict_file)
    assert type(dict_) == dict

