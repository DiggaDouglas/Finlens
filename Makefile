.PHONY: help setup verify-data test lint clean run-stub

PYTHON = venv/bin/python
PIP = venv/bin/pip
PYTEST = venv/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make setup        : Create virtual environment and install all dependencies"
	@echo "  make verify-data  : Validate scraped and segmented datasets"
	@echo "  make test         : Run unit tests"
	@echo "  make lint         : Run code style checks"
	@echo "  make run-stub     : Launch Streamlit interface placeholder"

setup:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm
	@echo "==> Environment ready."

verify-data:
	$(PYTHON) -c "import pandas as pd; df=pd.read_csv('data/processed/annotation_dataset.csv'); print(f'Dataset valid: {len(df)} clauses indexed.')"

test:
	$(PYTEST) tests/ -v

lint:
	$(PYTHON) -m flake8 src/ app/ tests/ --max-line-length=120 || true

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-stub:
	venv/bin/streamlit run app/main.py