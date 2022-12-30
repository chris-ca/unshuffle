#!/usr/bin/env python3
"""Tests for dictionary"""
import pytest

from unshuffle.dict_ import Dict, DictionaryConverter, FrequencyDictConverter


def test_read_dictionary_from_text(dict_contents):
    t = Dict(dict_contents)
    assert "Waceehhinnt" in t
    assert "Weihnachten" not in t


def test_read_dictionary_from_file(dict_file):
    t = Dict(dict_file)
    assert "Waceehhinnt" in t
    assert "Weihnachten" not in t


def test_make_dictionary(words_file, tmp_path):
    temp_dict = tmp_path / "temp_dict.txt"
    d = DictionaryConverter.from_type(
        "frequency", **{"frequency_file": words_file, "dict_file": temp_dict}
    )
    assert isinstance(d, FrequencyDictConverter)
    d.generate()
    assert "der" in d
    assert "SKIPPED" not in d


def test_parse_line_find_word():
    FrequencyDictConverter.parse_line("1000 normal 99999")


def test_parse_line_ignore_entries():
    with pytest.raises(ValueError):
        FrequencyDictConverter.parse_line("2 too many words 90")
    with pytest.raises(ValueError):
        FrequencyDictConverter.parse_line("1 a 90")
