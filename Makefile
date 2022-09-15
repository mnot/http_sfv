PROJECT=http_sfv
BLAB=blab
TESTS=test/tests/*.json

# for running from IDEs (e.g., TextMate)
.PHONY: run
run: test

.PHONY: test
test: $(TESTS) venv
	PYTHONPATH=.:$(VENV) $(VENV)/python test/test.py $(TESTS)
	PYTHONPATH=.:$(VENV) $(VENV)/python test/test_api.py

$(TESTS):
	git submodule update --init --recursive

.PHONY: update-tests
update-tests:
	cd test/tests; git pull origin main || exit
	git add test/tests
	git commit -m "update tests"

.PHONY: perf
perf: venv
	PYTHONPATH=$(VENV) $(VENV)/python test/test_perf.py

.PHONY: typecheck
typecheck: venv
	PYTHONPATH=$(VENV) $(VENV)/python -m mypy $(PROJECT)

.PHONY: fuzz
fuzz-%: venv
	$(BLAB) -l test/ -e "sf.sf-$*" | PYTHONPATH=$(VENV) $(VENV)/python -m http_sfv --$* --stdin

.PHONY: tidy
tidy: venv
	$(VENV)/black $(PROJECT)

.PHONY: lint
lint: venv
	PYTHONPATH=$(VENV) $(VENV)/pylint --output-format=colorized $(PROJECT)

.PHONY: clean
clean:
	find . -d -type d -name __pycache__ -exec rm -rf {} \;
	rm -rf build dist MANIFEST $(PROJECT).egg-info .venv .mypy_cache *.log


#############################################################################
## Distribution

.PHONY: version
version: venv
	$(eval VERSION=$(shell $(VENV)/python -c "import $(PROJECT); print($(PROJECT).__version__)"))

.PHONY: build
build: clean venv
	$(VENV)/python -m build

.PHONY: upload
upload: build test typecheck version
	git tag $(PROJECT)-$(VERSION)
	git push
	git push --tags origin
	$(VENV)/python -m twine upload dist/*



include Makefile.venv
