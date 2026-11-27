PYTHON ?= python3.15
.PHONY: install test

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m django test tests --settings=tests.test_settings
