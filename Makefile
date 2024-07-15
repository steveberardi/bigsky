PYTHONPATH=./src/
PYTHON=./venv/bin/python

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
	@$(PYTHON) src/bigsky/builders/tycho.py

db: venv/bin/activate
	@PYTHONPATH=./src/ $(PYTHON) src/bigsky/loaders/run.py raw/ dist/bigsky.db

build: venv/bin/activate
	$(PYTHON) -m flit build

publish: venv/bin/activate
	$(PYTHON) -m flit publish

clean:
	rm -rf __pycache__
	rm -rf venv

.PHONY: clean example db
