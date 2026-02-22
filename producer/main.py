"""
Kafka Word Producer – entry point.

Modes:
  urls.txt exists and has content → process listed URLs sequentially (cyclic)
  urls.txt missing / empty        → fetch random Wikipedia articles
"""
import logging
import sys
import time
from pathlib import Path
from typing import List

from config.settings import settings
from src.fetchers.wikipedia import WikipediaFetcher
from src.kafka.producer import KafkaWordProducer
from src.processors.word_filter import WordFilter

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def load_urls(filepath: str) -> List[str]:
    """Read urls.txt – skips blank lines and lines starting with #."""
    path = Path(filepath)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def main() -> None:
    urls = load_urls(settings.URLS_FILE)

    if urls:
        logger.info("URL mode: %d URL(s) loaded from '%s'", len(urls), settings.URLS_FILE)
        mode = "url"
    else:
        logger.info("Random mode: '%s' not found or empty", settings.URLS_FILE)
        mode = "random"

    fetcher = WikipediaFetcher(language=settings.WIKIPEDIA_LANGUAGE)
    word_filter = WordFilter(min_length=settings.WORD_MIN_LENGTH)
    producer = KafkaWordProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=settings.KAFKA_TOPIC,
        client_id=settings.KAFKA_CLIENT_ID,
    )

    logger.info(
        "Starting – brokers=%s  topic=%s  min_length=%d  interval=%ds",
        settings.KAFKA_BOOTSTRAP_SERVERS,
        settings.KAFKA_TOPIC,
        settings.WORD_MIN_LENGTH,
        settings.FETCH_INTERVAL,
    )

    try:
        index = 0
        while True:
            if mode == "url":
                url = urls[index % len(urls)]
                index += 1
                logger.info("Processing URL [%d/%d]: %s", index, len(urls), url)
                try:
                    sentences = fetcher.fetch_sentences_by_url(url)
                except Exception as exc:
                    logger.error("Skipping URL (%s): %s", url, exc)
                    time.sleep(settings.FETCH_INTERVAL)
                    continue
            else:
                try:
                    sentences = fetcher.fetch_sentences()
                except Exception as exc:
                    logger.error("Fetch error, skipping cycle: %s", exc)
                    time.sleep(settings.FETCH_INTERVAL)
                    continue

            _publish(sentences, word_filter, producer)
            logger.info("Sleeping %d s…", settings.FETCH_INTERVAL)
            time.sleep(settings.FETCH_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Shutting down…")
    finally:
        producer.flush()
        logger.info("Producer stopped.")


def _publish(
    sentences: List[str],
    word_filter: WordFilter,
    producer: KafkaWordProducer,
) -> None:
    total = 0
    for sentence in sentences:
        for word in word_filter.filter_sentence(sentence):
            producer.send(
                word=word,
                source="wikipedia",
                language=settings.WIKIPEDIA_LANGUAGE,
                sentence=sentence,
            )
            total += 1
    producer.flush()
    logger.info("Published %d word(s) from %d sentence(s)", total, len(sentences))


if __name__ == "__main__":
    main()