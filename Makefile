all: test run

py_env = echo activate virtual env here

run:
	@$(py_env) ; python3.6 ./src/main.py

test:
	@$(py_env) ; python3.6 -m unittest  discover -s src -p "*_test.py" -v

travis: travis_env all


travis_env:
	@$(eval py_env = : )


.PHONY: test run travis travis_run all
