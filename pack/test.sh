#!/bin/sh

PYTHONPATH="${PWD}/pybridge:${PWD}/tests:$PYTHONPATH"
python tests/test.py

