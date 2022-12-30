install:
	poetry install

format:
	black unshuffle/*.py tests/*.py
	#black --skip-string-normalization unshuffle/*.py

lint:
	mypy unshuffle
	flake8 $(git ls-files '*.py')
	pylint unshuffle
	# flake8 unshuffle test
	# pylint --disable=R,C ./hello

test:
	pytest --cov-report term-missing --cov	-v tests/

test_release:
	poetry publish --build -r testpypi

all: install lint test
