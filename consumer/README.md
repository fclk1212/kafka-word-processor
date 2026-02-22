# consumer/

> **Placeholder** – This directory is reserved for the Kafka consumer that will
> be implemented in a separate language (e.g. Go, Java, Node.js, Rust).

---

## What to implement here

Subscribe to the `filtered-words` Kafka topic and process the incoming word messages.

### Topic details

| Property | Value |
|----------|-------|
| Topic name | `filtered-words` |
| Key | word (UTF-8 string) |
| Value | JSON (UTF-8) – see schema below |

### Message schema

```json
{
  "word":     "python",
  "length":   6,
  "source":   "wikipedia",
  "language": "en",
  "sentence": "Python is a high-level programming language."
}
```

### Suggested consumer group ID

```
word-consumer-group
```

### Recommended Kafka client libraries by language

| Language | Library |
|----------|---------|
| Go | [confluent-kafka-go](https://github.com/confluentinc/confluent-kafka-go) |
| Java | [spring-kafka](https://spring.io/projects/spring-kafka) or [kafka-clients](https://mvnrepository.com/artifact/org.apache.kafka/kafka-clients) |
| Node.js | [kafkajs](https://kafka.js.org/) |
| Rust | [rdkafka](https://github.com/fede1024/rust-rdkafka) |
| .NET | [Confluent.Kafka](https://github.com/confluentinc/confluent-kafka-dotnet) |

---

## Connecting to Kafka

Kafka broker address (from inside Docker network):

```
kafka:9092
```

From your host machine:

```
localhost:9092
```

---

## Docker Compose integration

Uncomment the `consumer` service block in the root `docker-compose.yml`
and point it at your consumer's `Dockerfile`:

```yaml
consumer:
  build: ./consumer
  environment:
    - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    - KAFKA_TOPIC=filtered-words
    - KAFKA_GROUP_ID=word-consumer-group
  depends_on:
    kafka:
      condition: service_healthy
```
