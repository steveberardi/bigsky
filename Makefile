PYTHONPATH=./src/
PYTHON=./venv/bin/python
VERSION=$(shell python -c 'import src.bigsky as bigsky; print(bigsky.__version__)')
VERSION_CHECK=$(shell gh release list \
		-R steveberardi/bigsky \
		--limit 1000 \
		--json tagName \
		--jq '.[] | select(.tagName == "v$(VERSION)")' | wc -c)

# Development ------------------------------------------
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

clean:
	rm -rf __pycache__
	rm -rf venv

# Builders ------------------------------------------
stars: venv/bin/activate
	@mkdir -p build
	@$(PYTHON) src/bigsky/builders/stars.py
	@gzip -fk build/bigsky.stars.csv
	@gzip -fk build/bigsky.stars.mag11.csv

# Releases ------------------------------------------
release-check:
	@CHECK="$(VERSION_CHECK)";  \
	if [ $$CHECK -eq 0 ] ; then \
		echo "version check passed!"; \
	else \
		echo "version tag already exists"; \
		false; \
	fi

release: release-check test stars
	gh release create \
		v$(VERSION) \
		build/bigsky.stars.csv.gz \
		build/bigsky.stars.mag11.csv.gz \
		docs/stars.md \
		--title "v$(VERSION)" \
		-R steveberardi/bigsky

version: venv/bin/activate
	@echo $(VERSION)

# Deprecated? ------------------------------------------
db: venv/bin/activate
	@PYTHONPATH=./src/ $(PYTHON) src/bigsky/loaders/run.py raw/ dist/bigsky.db

build: venv/bin/activate
	$(PYTHON) -m flit build

publish: venv/bin/activate
	$(PYTHON) -m flit publish

.PHONY: clean example db test stars release release-check
