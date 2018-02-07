all: test run

py_env =  echo activate virtual env here
py_exe := python

run:
	@$(py_env) ; $(py_exe) ./src/main.py

test:
	@$(py_env) ; $(py_exe) -m unittest  discover -s src -p "*_test.py" -v

travis: travis_env all

travis_env:
	@$(eval py_env = : )


.PHONY: test run travis travis_run all
