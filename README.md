# kafka-word-processor

> 🇹🇷 Türkçe dokümantasyon için [README.tr.md](README.tr.md) dosyasına bakın.

A monorepo for a Kafka-based word-processing pipeline that fetches Wikipedia articles, filters words by minimum length, and publishes them to a Kafka topic.

```
Wikipedia API  ──▶  [producer]  ──▶  Kafka Topic: filtered-words  ──▶  [consumer *]
                    (Python)                                              (any language)
```

> `*` The consumer lives in `consumer/` and will be implemented in a separate language.
> Kafka is managed **externally** – this project only contains application code.

---

## Repository structure

```
kafka-word-processor/
├── Makefile                  # Developer shortcuts
├── .env.example              # Environment variable template
├── .gitignore
│
├── producer/                 # Python Kafka producer
│   ├── Dockerfile            # (optional) containerise the producer
│   ├── main.py               # Entry point
│   ├── urls.txt              # Wikipedia URLs to process (one per line)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── config/
│   │   └── settings.py       # Pydantic-settings config (env vars / .env)
│   ├── src/
│   │   ├── fetchers/
│   │   │   └── wikipedia.py  # Wikipedia REST API client
│   │   ├── processors/
│   │   │   └── word_filter.py # Min-length word filter
│   │   └── kafka/
│   │       └── producer.py   # confluent-kafka producer wrapper
│   └── tests/
│       ├── test_word_filter.py
│       └── test_wikipedia_fetcher.py
│
└── consumer/                 # Placeholder – future consumer (any language)
    └── README.md
```

---

## Quick start

### Prerequisites

- Python 3.12+
- A running Kafka broker (any version ≥ 3.x)

### 1 – Configure

```bash
cp .env.example .env
# Set KAFKA_BOOTSTRAP_SERVERS to your broker address
```

### 2 – Add Wikipedia URLs

Edit `producer/urls.txt` – one URL per line:

```
https://en.wikipedia.org/wiki/Istanbul
https://en.wikipedia.org/wiki/Apache_Kafka
https://tr.wikipedia.org/wiki/Türkiye
```

If the file is left empty, the producer falls back to fetching **random** articles.

### 3 – Install dependencies

```bash
make install
# or: python3 -m pip install -r producer/requirements.txt
```

### 4 – Run

```bash
make run
# or: cd producer && python3 main.py
```

### 5 – Watch messages

```bash
make topic-watch
```

---

## How it works

```
1. Read urls.txt
       │
       ├─ URLs found  → fetch each article in order, loop back to start
       └─ Empty / missing → fetch a random Wikipedia article
       │
2. Split article text into sentences
3. Filter words: keep only tokens with length >= WORD_MIN_LENGTH
4. Publish each word as a JSON message to Kafka
5. Wait FETCH_INTERVAL seconds → repeat
```

---

## Message schema

```json
{
  "word":     "python",
  "length":   6,
  "source":   "wikipedia",
  "language": "en",
  "sentence": "Python is a high-level programming language."
}
```

Key: the word itself (UTF-8). Value: JSON (UTF-8). Any consumer in any language can deserialise this with a standard JSON library.

---

## Configuration reference

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker address(es) |
| `KAFKA_TOPIC` | `filtered-words` | Target topic |
| `KAFKA_CLIENT_ID` | `word-producer` | Producer client ID |
| `WIKIPEDIA_LANGUAGE` | `en` | Fallback language for random mode |
| `URLS_FILE` | `urls.txt` | Path to the URL list file |
| `WORD_MIN_LENGTH` | `5` | Minimum character count for a word |
| `FETCH_INTERVAL` | `30` | Seconds between fetch cycles |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## Running tests

```bash
make install-dev
make test
```

---

## Adding a consumer

1. Create your consumer project under `consumer/` (any language).
2. Subscribe to the `filtered-words` topic using group ID `word-consumer-group`.
3. See `consumer/README.md` for the full message schema and recommended libraries.

---

## Tech stack

| Component | Technology |
|-----------|-----------|
| Message broker | External Kafka (≥ 3.x) |
| Producer | Python 3.12 + confluent-kafka 2.4 |
| Config | pydantic-settings |
| HTTP | requests + urllib3 retry |
| Tests | pytest + responses (mock) |
| Lint / format | ruff |
| Type check | mypy |