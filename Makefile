# ─────────────────────────────────────────────────────────────────────────────
#  kafka-word-processor – Developer shortcuts
#  Assumes Kafka is already running externally.
#  Configure broker address via KAFKA_BOOTSTRAP_SERVERS in .env
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help run install install-dev test lint typecheck \
        topic-list topic-watch

PRODUCER_DIR = producer
PYTHON       = python3

# Default target
help:
	@echo ""
	@echo "  make install       – Install producer runtime dependencies"
	@echo "  make install-dev   – Install dev + test dependencies"
	@echo "  make run           – Run the producer locally"
	@echo "  make test          – Run unit tests with coverage"
	@echo "  make lint          – Run ruff linter + format check"
	@echo "  make typecheck     – Run mypy type checker"
	@echo "  make topic-list    – List Kafka topics (requires kafka-topics.sh on PATH)"
	@echo "  make topic-watch   – Tail filtered-words topic (requires kafka-console-consumer.sh)"
	@echo ""

# ── Producer ──────────────────────────────────────────────────────────────────
install:
	pip3 install -r $(PRODUCER_DIR)/requirements.txt

install-dev:
	pip3 install -r $(PRODUCER_DIR)/requirements-dev.txt

run:
	cd $(PRODUCER_DIR) && $(PYTHON) main.py

# ── Tests & code quality ─────────────────────────────────────────────────────
test:
	cd $(PRODUCER_DIR) && $(PYTHON) -m pytest

lint:
	cd $(PRODUCER_DIR) && ruff check . && ruff format --check .

typecheck:
	cd $(PRODUCER_DIR) && mypy src config main.py --ignore-missing-imports

# ── Kafka helpers (uses Kafka CLI tools – must be on PATH) ────────────────────
KAFKA_BROKER ?= localhost:9092
KAFKA_TOPIC  ?= filtered-words

topic-list:
	kafka-topics.sh --bootstrap-server $(KAFKA_BROKER) --list

topic-watch:
	kafka-console-consumer.sh \
		--bootstrap-server $(KAFKA_BROKER) \
		--topic $(KAFKA_TOPIC) \
		--from-beginning \
		--property print.key=true \
		--property key.separator=" → "
