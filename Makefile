PYTHONPATH=./src/
PYTHON=./venv/bin/python
VERSION=$(shell python -c 'import src.bigsky.builders.tycho as bigsky; print(bigsky.__version__)')
VERSION_CHECK=$(shell gh release list \
		-R steveberardi/starplot \
		--json tagName \
		--jq '.[] | select(.tagName == "v0.3.0b")' | wc -c)
# TODO : change above to bigsky repo

install: venv/bin/activate

lint: venv/bin/activate
	@$(PYTHON) -m ruff check src/ $(ARGS)

format: venv/bin/activate
	@$(PYTHON) -m black src/ $(ARGS)

test: venv/bin/activate
	PYTHONPATH=./src/ $(PYTHON) -m pytest --cov=src/ --cov-report=term --cov-report=html src/

venv/bin/activate: requirements.txt
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

shell: venv/bin/activate
	@PYTHONPATH=./src/ $(PYTHON)

tycho: venv/bin/activate
	@mkdir -p build
	@$(PYTHON) src/bigsky/builders/tycho.py
	@gzip -fk build/tycho2.stars.csv
	@gzip -fk build/tycho2.stars.mag11.csv

release-check:
	@CHECK="$(VERSION_CHECK)";  \
	if [ $$CHECK -eq 0 ] ; then \
		echo "version check passed!"; \
	else \
		echo "version tag already exists"; \
		false; \
	fi

release: release-check test tycho
	gh release create \
		v$(VERSION) \
		build/tycho2.stars.csv.gz \
		build/tycho2.stars.mag11.csv.gz \
		--title "v$(VERSION)" \
		-R steveberardi/bigsky

db: venv/bin/activate
	@PYTHONPATH=./src/ $(PYTHON) src/bigsky/loaders/run.py raw/ dist/bigsky.db

build: venv/bin/activate
	$(PYTHON) -m flit build

publish: venv/bin/activate
	$(PYTHON) -m flit publish

clean:
	rm -rf __pycache__
	rm -rf venv

.PHONY: clean example db test tycho release release-check
