PROJECT=http_sfv
BLAB=test/blab
TESTS=test/tests/*.json

# for running from IDEs (e.g., TextMate)
.PHONY: run
run: test

.PHONY: test
test: $(TESTS) venv
	PYTHONPATH=.:$(VENV) $(VENV)/python test/test.py $(TESTS)

$(TESTS):
	git submodule update --init --recursive

.PHONY: update-tests
update-tests:
	cd test/tests; git pull origin main || exit
	git add test/tests
	git commit -m "update tests"

.PHONY: perf
perf: venv
	PYTHONPATH=. $(VENV)/python test/test_perf.py

.PHONY: typecheck
typecheck: venv
	PYTHONPATH=$(VENV) $(VENV)/python -m mypy $(PROJECT)

pyright: venv
	PYTHONPATH=$(VENV) $(VENV)/python -m pyright $(PROJECT)

$(BLAB).c:
	curl https://haltp.org/files/blab-0.2.c.gz | gzip -d > $@

$(BLAB): $(BLAB).c
	sha256sum -c test/download.sha256 && cc -O -o $@ $<

.PHONY: fuzz-%
fuzz-%: venv $(BLAB)
	while [ true ];\
	do\
		$(BLAB) -l test -e "sf.sf-$*" -f 200 | PYTHONPATH=$(VENV) $(VENV)/python -m http_sfv --$* --stdin || exit 1;\
	done

.PHONY: tidy
tidy: venv
	$(VENV)/black $(PROJECT)

.PHONY: lint
lint: venv
	PYTHONPATH=$(VENV) $(VENV)/pylint --output-format=colorized $(PROJECT)

.PHONY: clean
clean: clean-venv
	find . -d -type d -name __pycache__ -exec rm -rf {} \;
	rm -rf build dist MANIFEST $(PROJECT).egg-info .mypy_cache *.log test/blab*


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
