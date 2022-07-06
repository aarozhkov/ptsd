.PHONY: local-dev fix check typing unit_adapter unit_scheduler supervisor


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

unit_adapter:
	pytest --ignore=tests/integration --ignore=tests/supervisor --ignore=tests/shared --ignore=tests/scheduler

unit_scheduler:
	pytest --ignore=tests/integration --ignore=tests/supervisor --ignore=tests/shared --ignore=tests/adapter


supervisor:
	uvicorn supervisor:app --reload
