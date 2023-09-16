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

.PHONY: clean
clean: clean_py
	rm -rf test/blab*

.PHONY: tidy
tidy: tidy_py

.PHONY: lint
lint: lint_py

.PHONY: typecheck
typecheck: typecheck_py

#############################################################################
## Distribution

.PHONY: upload
upload: build test typecheck version
	git tag $(PROJECT)-$(VERSION)
	git push
	git push --tags origin
	$(VENV)/python -m twine upload dist/*


include Makefile.pyproject
