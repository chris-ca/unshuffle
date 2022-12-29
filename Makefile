install:
	poetry install

format:
	black --skip-string-normalization unshuffle/*.py

lint:
	flake8 unshuffle
	pylint unshuffle
	# pylint --disable=R,C ./hello

test:
	pytest --cov-report term-missing --cov	-v tests/

test_release:
	poetry publish --build -r testpypi

all: install lint test
