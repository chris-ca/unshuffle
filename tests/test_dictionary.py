#!/usr/bin/env python3
import pytest

from unshuffle.dict_ import Dict, DictionaryConverter, FrequencyDictConverter


def test_read_dictionary_from_text(dict_contents):
    t = Dict(dict_contents)
    assert 'Waceehhinnt' in t
    assert 'Weihnachten' not in t


def test_read_dictionary_from_file(dict_file):
    t = Dict(dict_file)
    assert type(t.dictionary) == dict


def test_make_dictionary(words_file, tmp_path):
    temp_dict = tmp_path / 'temp_dict.txt'
    d = FrequencyDictConverter(words_file, temp_dict)
    d.generate()
    assert 'der' in d
    assert 'SKIPPED' not in d


def test_create_object():
    assert isinstance(
        DictionaryConverter.from_type(
            'frequency', {'frequency_file': None, 'dict_file': None}
        ),
        FrequencyDictConverter,
    )


def test_parse_line_find_word():
    FrequencyDictConverter.parse_line('1000 normal 99999')


def test_parse_line_ignore_entries():
    with pytest.raises(ValueError):
        FrequencyDictConverter.parse_line('2 too many words 90')
    with pytest.raises(ValueError):
        FrequencyDictConverter.parse_line('1 a 90')
