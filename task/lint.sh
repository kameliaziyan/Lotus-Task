#!/bin/bash

echo "Running flake8 with \"wemake-python-styleguide (WPS)\" plugin"
flake8 . --select=WPS

echo "Running mypy"
mypy --exclude-gitignore . 