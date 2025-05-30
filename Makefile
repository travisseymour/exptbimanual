# Makefile
# --------
# Usage:
# make [COMMAND]
# E.g.:
# make format

.PHONY: help install format build clean test clean-pycache format

help:
	clear
	head Makefile

install:
	pip install -U pip wheel
	pip install .[dev]
	pip uninstall exptbimanual -y
	make clean

format:
	ruff check exptbimanual --fix
	ruff format exptbimanual
	black exptbimanual

build:
	python -m build

clean:
	rm -rf build dist *.egg-info

test:
	PYTHONPATH=$(shell pwd) pytest tests/

clean-pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} +

update-exptsys:
	pip install -U pip wheel exptsys
