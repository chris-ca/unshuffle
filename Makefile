install:
	pip install -r requirements.txt

format:
	black *.py

lint:
	pylint ./unshuffle.py
	# pylint --disable=R,C ./hello

test:
	python -m pytest -v tests/

all: install lint test
