#!/usr/bin/env make

HOME = ./
NAME = anna-molly
TEST = ./test/

.PHONY:clean test docs

init:
	pip install -r requirements.txt

clean:
	-rm $(HOME)*.pyc

test:
	make -C $(TEST)
