"""
Kafka producer wrapper.

Sends word messages to the configured topic using confluent-kafka.
Each message value is a JSON object so future consumers (in any language)
can deserialise it with a standard JSON library.

Message schema
--------------
{
  "word":     "hello",          # the filtered word
  "length":   5,                # character count
  "source":   "wikipedia",      # data source identifier
  "language": "en",             # Wikipedia language code
  "sentence": "Hello world..."  # originating sentence (optional context)
}
"""
import json
import logging
from typing import Optional

from confluent_kafka import Producer, KafkaException

logger = logging.getLogger(__name__)


class KafkaWordProducer:
    """Thread-safe Kafka producer for word messages."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        client_id: str = "word-producer",
    ):
        self.topic = topic
        self._producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "client.id": client_id,
                # Reliability settings
                "acks": "all",
                "retries": 5,
                "retry.backoff.ms": 300,
                # Throughput / latency tuning
                "linger.ms": 20,
                "batch.size": 16384,
                "compression.type": "lz4",
            }
        )
        logger.info(
            "KafkaWordProducer ready – brokers=%s  topic=%s",
            bootstrap_servers,
            topic,
        )

    # ── Public interface ─────────────────────────────────────────────────────

    def send(
        self,
        word: str,
        source: str = "wikipedia",
        language: str = "en",
        sentence: Optional[str] = None,
    ) -> None:
        """Produce a single word message (non-blocking)."""
        payload = {
            "word": word,
            "length": len(word),
            "source": source,
            "language": language,
            "sentence": sentence,
        }
        try:
            self._producer.produce(
                topic=self.topic,
                key=word.encode("utf-8"),
                value=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                on_delivery=self._on_delivery,
            )
            # Trigger delivery callbacks without blocking.
            self._producer.poll(0)
        except KafkaException as exc:
            logger.error("Failed to produce message for word '%s': %s", word, exc)
            raise

    def flush(self, timeout: float = 10.0) -> None:
        """Block until all in-flight messages are delivered."""
        remaining = self._producer.flush(timeout=timeout)
        if remaining:
            logger.warning(
                "%d message(s) were not delivered within %.1f s", remaining, timeout
            )

    # ── Callbacks ────────────────────────────────────────────────────────────

    @staticmethod
    def _on_delivery(err, msg) -> None:
        if err:
            logger.error(
                "Delivery failed – topic=%s partition=%s: %s",
                msg.topic(),
                msg.partition(),
                err,
            )
        else:
            logger.debug(
                "Delivered – topic=%s partition=%d offset=%d key=%s",
                msg.topic(),
                msg.partition(),
                msg.offset(),
                msg.key().decode("utf-8"),
            )
