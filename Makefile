PYTHON=python3
PYTHONPATH=./
name=shhh
version=$(shell PYTHONPATH=$(PYTHONPATH) $(PYTHON) -c "import $(name); print($(name).__version__)")

# for running from IDEs (e.g., TextMate)
.PHONY: run
run: test

.PHONY: version
version:
	@echo $(version)

.PHONY: dist
dist: clean typecheck # test
	git tag $(name)-$(version)
	git push
	git push --tags origin
	$(PYTHON) setup.py sdist
	$(PYTHON) -m twine upload dist/*

.PHONY: lint
lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pylint --rcfile=test/pylintrc $(name)

.PHONY: black
black:
	PYTHONPATH=$(PYTHONPATH) black shhh/*.py

.PHONY: test
test: test/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) test/test.py

test/tests:
	git submodule update --init --recursive

.PHONY: typecheck
typecheck:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m mypy --config-file=test/mypy.ini $(name)

.PHONY: clean
clean:
	rm -rf build dist MANIFEST $(name).egg-info
	find . -type f -name \*.pyc -exec rm {} \;
	find . -d -type d -name __pycache__ -exec rm -rf {} \;
