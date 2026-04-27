COMPOSE_BASE = docker compose -f docker-compose.yml
COMPOSE_TEST = docker compose -f docker-compose.yml -f docker-compose.test.yml

.PHONY: verify-test-override test-config test-up test-restart test-ps test-logs

verify-test-override:
	python3 tools/verify_test_override.py

test-config: verify-test-override
	$(COMPOSE_TEST) config

test-up: verify-test-override
	$(COMPOSE_TEST) up -d

test-restart: verify-test-override
	$(COMPOSE_TEST) up -d --force-recreate ripper flac_mirror

test-ps: verify-test-override
	$(COMPOSE_TEST) ps

test-logs: verify-test-override
	$(COMPOSE_TEST) logs --tail=100 ripper flac_mirror
