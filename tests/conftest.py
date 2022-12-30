#!/usr/bin/env python3
"""Shared test configuration."""
import pytest
from unshuffle.unshuffle import Text
from unshuffle.dict_ import Dict


@pytest.fixture
def words_file():
    return "tests/fixtures/frequency.txt"


@pytest.fixture(name="dict_contents")
def fixture_dict_contents():
    return """der der 134545
dei die 128801
dnu und 98167
in in 79568
den den 51249
uz zu 41735
nov von 40962
ads das 40670
im im 36656
Dei Die 34045
Hallo hallo 30855
Waceehhinnt Weihnachten 308
orv vor 13365
ehstt steht 2625
Oenrst Ostern 176
Terü Türe 13
Wir Wir 100
nsu uns 98167
eefnru freuen 100
-BKaeeeklnrsstu Bernkastel-Kues 200
deor oder 100"""


@pytest.fixture
def dict_file(dict_contents, tmp_path):
    df = tmp_path / "dict.txt"
    with open(df, "w", encoding="utf-8") as f:
        f.write(dict_contents)
        return str(df)


@pytest.fixture(name="dict_")
def fixture_dict_(dict_contents):
    return Dict(dict_contents)


@pytest.fixture
def text(dict_):
    return Text(dict_)
