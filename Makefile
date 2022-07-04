.PHONY: style check-style start install develop test load-test
style:
	# apply opinionated styles
	@black api
	@isort api

	# tests are production code too!
	@black tests
	@isort tests

check-style:
	@black api --check
	@flake8 api --count --show-source --statistics --ignore=E203,W503

start:
	@bash bin/run.sh

install:
	@pip install -r requirements.txt

develop:
	@pip install -r requirements.txt

docker-build:
	@docker build . -t ocrosby/soccer-api

docker-run: docker-build
	@docker run -p 8080:8080 ocrosby/soccer-api

test:
	@pytest tests

load-test:
	@locust -f tests/load/locustfiles/api.py
