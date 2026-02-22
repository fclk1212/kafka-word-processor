# kafka-word-processor

> 🇬🇧 For English documentation see [README.md](README.md).

Wikipedia makalelerinden cümle çeken, kelimeleri minimum uzunluğa göre filtreleyen ve Kafka topic'ine gönderen bir pipeline.

```
Wikipedia API  ──▶  [producer]  ──▶  Kafka Topic: filtered-words  ──▶  [consumer *]
                    (Python)                                              (herhangi bir dil)
```

> `*` Consumer `consumer/` klasöründe yer alacak, farklı bir dilde yazılacak.
> Kafka **harici** olarak yönetilir – bu proje yalnızca uygulama kodunu içerir.

---

## Proje yapısı

```
kafka-word-processor/
├── Makefile                  # Geliştirici kısayolları
├── .env.example              # Ortam değişkenleri şablonu
├── .gitignore
│
├── producer/                 # Python Kafka producer
│   ├── Dockerfile            # (isteğe bağlı) producer'ı container'a al
│   ├── main.py               # Giriş noktası
│   ├── urls.txt              # İşlenecek Wikipedia URL'leri (her satıra bir tane)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── config/
│   │   └── settings.py       # Pydantic-settings ile config yönetimi
│   ├── src/
│   │   ├── fetchers/
│   │   │   └── wikipedia.py  # Wikipedia REST API istemcisi
│   │   ├── processors/
│   │   │   └── word_filter.py # Minimum uzunluk filtresi
│   │   └── kafka/
│   │       └── producer.py   # confluent-kafka producer sarmalayıcı
│   └── tests/
│       ├── test_word_filter.py
│       └── test_wikipedia_fetcher.py
│
└── consumer/                 # Gelecekte eklenecek consumer (herhangi bir dil)
    └── README.md
```

---

## Hızlı başlangıç

### Gereksinimler

- Python 3.12+
- Çalışan bir Kafka broker (≥ 3.x)

### 1 – Yapılandırma

```bash
cp .env.example .env
# KAFKA_BOOTSTRAP_SERVERS değerini kendi broker adresinizle güncelleyin
```

### 2 – Wikipedia URL'lerini ekle

`producer/urls.txt` dosyasını düzenleyin – her satıra bir URL:

```
https://en.wikipedia.org/wiki/Istanbul
https://en.wikipedia.org/wiki/Apache_Kafka
https://tr.wikipedia.org/wiki/Türkiye
```

Dosya boş bırakılırsa producer **rastgele** makale çekme moduna geçer.

### 3 – Bağımlılıkları kur

```bash
make install
# veya: python3 -m pip install -r producer/requirements.txt
```

### 4 – Çalıştır

```bash
make run
# veya: cd producer && python3 main.py
```

### 5 – Mesajları izle

```bash
make topic-watch
```

---

## Nasıl çalışır?

```
1. urls.txt okunur
       │
       ├─ URL varsa   → makaleler sırayla işlenir, sona gelince başa döner
       └─ Boş / yoksa → rastgele Wikipedia makalesi çekilir
       │
2. Makale metni cümlelere bölünür
3. Kelimeler filtrelenir: yalnızca uzunluğu >= WORD_MIN_LENGTH olanlar alınır
4. Her kelime JSON mesajı olarak Kafka'ya gönderilir
5. FETCH_INTERVAL saniye beklenir → tekrar başa döner
```

---

## Mesaj şeması

```json
{
  "word":     "python",
  "length":   6,
  "source":   "wikipedia",
  "language": "en",
  "sentence": "Python is a high-level programming language."
}
```

Anahtar: kelimenin kendisi (UTF-8). Değer: JSON (UTF-8). Herhangi bir dildeki consumer standart bir JSON kütüphanesiyle okuyabilir.

---

## Yapılandırma referansı

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker adresi |
| `KAFKA_TOPIC` | `filtered-words` | Hedef topic |
| `KAFKA_CLIENT_ID` | `word-producer` | Producer istemci kimliği |
| `WIKIPEDIA_LANGUAGE` | `en` | Rastgele mod için varsayılan dil |
| `URLS_FILE` | `urls.txt` | URL listesi dosyasının yolu |
| `WORD_MIN_LENGTH` | `5` | Kabul edilecek minimum kelime uzunluğu |
| `FETCH_INTERVAL` | `30` | Döngüler arası bekleme süresi (saniye) |
| `LOG_LEVEL` | `INFO` | Python log seviyesi |

---

## Testleri çalıştırma

```bash
make install-dev
make test
```

---

## Consumer ekleme

1. `consumer/` klasörü altında consumer projenizi oluşturun (herhangi bir dil).
2. `filtered-words` topic'ine `word-consumer-group` grup ID'siyle abone olun.
3. Mesaj şeması ve önerilen kütüphaneler için `consumer/README.md` dosyasına bakın.

---

## Teknoloji yığını

| Bileşen | Teknoloji |
|---------|----------|
| Mesaj aracısı | Harici Kafka (≥ 3.x) |
| Producer | Python 3.12 + confluent-kafka 2.4 |
| Config | pydantic-settings |
| HTTP | requests + urllib3 retry |
| Testler | pytest + responses (mock) |
| Linter / format | ruff |
| Tip kontrolü | mypy |