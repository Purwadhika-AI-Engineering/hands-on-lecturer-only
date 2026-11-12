# Convenience wrappers. No `make`? Every target is just the docker compose command shown.
.PHONY: up down logs reset test test-defenses attack compare

up:              ## build and start AcmeBot on http://localhost:8000
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f app

reset:           ## restore database, outbox, uploads and knowledge base
	curl -s -X POST http://localhost:8000/admin/reset

test:            ## offline sanity checks (no API key needed, no cost)
	docker compose run --rm -e LLM_MODE=fake app python -m pytest tests/test_plumbing.py -q

test-defenses:   ## offline security tests: FAIL until your guards work
	docker compose run --rm -e LLM_MODE=fake app python -m pytest tests/test_defenses.py -v

attack:          ## run the promptfoo attack suite against the real model. Save a named run: make attack NAME=before
	NAME=$(or $(NAME),latest) docker compose --profile tools run --rm promptfoo

compare:         ## pass-rate before vs after: make compare
	python3 scripts/compare.py promptfoo/results/before.json promptfoo/results/after.json


