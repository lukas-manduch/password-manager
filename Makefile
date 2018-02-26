py_env = echo activate virtual env here
py_exe = python
files = $(wildcard src/*.py)

all: test lint

run:
	@$(py_env) && $(py_exe) ./src/main.py

test:
	@$(py_env) && $(py_exe) -m unittest  discover -s src -p "*_test.py" -v

install:
	$(py_exe) -m pip install --user pylint

lint: $(files)

$(files):
	pylint $@

travis: install all

.PHONY: test run travis all $(files)
