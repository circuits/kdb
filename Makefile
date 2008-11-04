.PHONY: all clean checks tests

all: clean checks tests

clean:
	@rm -rf build dist kdb.egg-info
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

checks:
	@find . -name "*.py" -exec pyflakes {} +

tests:
	@nosetests --with-coverage
