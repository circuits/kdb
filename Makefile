.PHONY: help clean docs tests packages

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean     to cleanup build and temporary files"
	@echo "  docs      to build the documentation"
	@echo "  tests     to run the test suite"
	@echo "  packages  to build python source and egg packages"

clean:
	@rm -rf build dist kdb.egg-info
	@rm -rf .coverage coverage
	@rm -rf docs/build
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

docs:
	@make -C docs html

packages:
	@tools/mkpkgs -p python2.5
	@tools/mkpkgs -p python2.6

tests:
	@py.test -x -r fsxX \
		--ignore=tmp \
		--pastebin=all \
        tests/
