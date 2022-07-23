.venv:
	python -m venv .venv

.venv/deps: .venv setup.py setup.cfg
	.venv/bin/python -m pip install . build httpretty mock pytest nose
	touch .venv/deps

build: .venv/deps
	rm -rf ./dist/
	.venv/bin/python -m build .

# only works with python 3+
lint: .venv/deps
	.venv/bin/python -m pip install black==22.3.0
	.venv/bin/python -m black .

lint-check: .venv/deps
	.venv/bin/python -m pip install black==22.3.0
	.venv/bin/python -m black --check .

test: .venv/deps
	.venv/bin/python -m pytest sprinter tests

ready-pr: test lint