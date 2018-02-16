py_env = echo activate virtual env here
py_exe = python

all: test run

run:
	@$(py_env) && $(py_exe) ./src/main.py

test:
	@$(py_env) && $(py_exe) -m unittest  discover -s src -p "*_test.py" -v

travis: all

.PHONY: test run travis all
