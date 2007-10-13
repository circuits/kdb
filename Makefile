#
# Makefile for kdb
# ~~~~~~~~~~~~~~~~
#
# Combines scripts for common tasks.
#
# :copyright: 2007 by James Mills
# :license: GNU GPL, see LICENSE for more details.
#

PYTHON ?= python

export PATH=$(shell echo "$$HOME/bin:$$PATH")

export PYTHONPATH=$(shell echo "$$PYTHONPATH"):$(shell python -c 'import os; print ":".join(os.path.abspath(line.strip()) for line in file("PYTHONPATH"))' 2>/dev/null)

.PHONY: all apidocs clean clean-pyc epydoc pyflakes test

all: clean-pyc pyflakes test

apidocs: epydoc

clean: clean-pyc
	rm -rf apidocs
	rm -rf build dist kdb.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

epydoc:
	@rm -rf apidocs
	@$(PYTHON) -Wi:default_transform `which epydoc` \
		-o apidocs  \
		--url http://trac.shortcircuit.net.au/kdb \
		--no-frames --docformat restructuredtext \
		-v kdb
	@sed -i -e 's|^<br />||' \
			-e 's|\s\+$$||' \
			-e 's|^\s\+</pre>|</pre>|' \
			-e 's|\(<table class="[^"]*"\) border="1"|\1|' \
			-e 's|\(<table class="navbar" .*\) width="100%"|\1|' \
			-e 's|<td width="15%"|<td class="spacer"|' \
			apidocs/*.html
	@fix_epydoc_markup.py apidocs

pyflakes:
	@find . -name "*.py" -exec pyflakes {} +

test:
	@$(PYTHON) kdb/tests/run.py $(TESTS)
