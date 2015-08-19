#!/usr/bin/env make

init:
	pip install -r requirements.txt

clean:
	find . -type f -name '*.pyc' -delete

test:
	nosetests -v

.PHONY: test
