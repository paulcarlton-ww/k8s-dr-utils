

VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3

setup-dev:
	#TODO: add any other setup
	make venv

venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: setup.py
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	${PYTHON} -m pip install -U pip setuptools
	${VENV_NAME}/bin/pip install --editable .[dev]
	touch $(VENV_NAME)/bin/activate

test: venv
	${PYTHON} -m pytest

coverage: venv
	${PYTHON} -m pytest --cov=utilslib

coverage-report: venv
	${PYTHON} -m pytest --cov=utilslib --cov-report html

lint: venv
	${PYTHON} -m pylint --rcfile=pylintrc utilslib

