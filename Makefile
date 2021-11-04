.PHONY: local-dev fix check typing unit supervisor


local-dev:
	python3.9 -m venv venv
	. ./venv/bin/activate
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

fix:
	isort .
	black .


check:
	isort --check .
	black --check .

typing:
	mypy --check --exclude 'venv\/'

unit:
	pytest --ignore=tests/integration

supervisor:
	uvicorn supervisor:app --reload
