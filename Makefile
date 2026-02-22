.PHONY: help install lint format clean run venv

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
RUFF := $(VENV)/bin/ruff

help:
	@echo "Available commands:"
	@echo "  make venv          - Create virtual environment"
	@echo "  make install       - Install dependencies in venv"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with ruff"
	@echo "  make clean         - Remove venv and cache files"
	@echo "  make run           - Run Streamlit app"

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install -r requirements.txt
	$(PIP) install ruff

lint: install
	$(RUFF) check .

format: install
	$(RUFF) format .
	$(RUFF) check . --fix

clean:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

run: install
	$(PYTHON) -m streamlit run app.py
