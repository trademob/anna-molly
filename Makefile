#!/usr/bin/env make

init:
	pip install -r requirements.txt

clean:
	find . -type f -name '*.pyc' -delete

test:
	python -m unittest discover --verbose

.PHONY: test
