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

scratchpad: venv/bin/activate
	@PYTHONPATH=./src/ $(PYTHON) scratchpad.py

clean:
	rm -rf __pycache__
	rm -rf venv

# Builders ------------------------------------------
stars: venv/bin/activate
	@mkdir -p build
	@PYTHONPATH=./src/ $(PYTHON) src/bigsky/builders/stars.py

# Releases ------------------------------------------
release-check:
	@CHECK="$(VERSION_CHECK)";  \
	if [ $$CHECK -eq 0 ] ; then \
		echo "version check passed!"; \
	else \
		echo "version tag already exists"; \
		false; \
	fi

release: release-check test 
	@gzip -fk build/bigsky.$(VERSION).stars.csv
	@gzip -fk build/bigsky.$(VERSION).stars.mag11.csv
	gh release create \
		v$(VERSION) \
		build/bigsky.$(VERSION).stars.csv.gz \
		build/bigsky.$(VERSION).stars.mag11.csv.gz \
		docs/stars.md \
		--title "v$(VERSION)" \
		-R steveberardi/bigsky

version: venv/bin/activate
	@echo $(VERSION)


.PHONY: clean example db test stars release release-check
