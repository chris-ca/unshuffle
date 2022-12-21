install:
	poetry install

format:
	black unshuffle/*.py

lint:
	pylint unshuffle
	# pylint --disable=R,C ./hello

test:
	python -m pytest -v tests/

all: install lint test
