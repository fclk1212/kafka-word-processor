"""
Wikipedia REST API fetcher.

Desteklenen modlar:
  - fetch_sentences()          → rastgele makale
  - fetch_sentences_by_url()   → verilen Wikipedia URL'sinden makale
"""
import re
import logging
from typing import List
from urllib.parse import urlparse, unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

_SENTENCE_SPLITTER = re.compile(r"(?<=[.!?])\s+")


class WikipediaFetcher:

    def __init__(self, language: str = "en", timeout: int = 10):
        self.language = language
        self.timeout = timeout
        self._random_url = (
            f"https://{language}.wikipedia.org/api/rest_v1/page/random/summary"
        )
        self._session = self._build_session()

    # ── Public interface ─────────────────────────────────────────────────────

    def fetch_sentences(self) -> List[str]:
        """Rastgele Wikipedia makalesinden cümleler döndürür."""
        data = self._get_json(self._random_url)
        return self._extract_sentences(data)

    def fetch_sentences_by_url(self, url: str) -> List[str]:
        """Verilen Wikipedia URL'sinden cümleler döndürür.

        Desteklenen URL formatları:
          https://en.wikipedia.org/wiki/Python_(programming_language)
          https://tr.wikipedia.org/wiki/Türkiye
        """
        title = self._extract_title(url)
        language = self._extract_language(url)
        api_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{title}"
        logger.info("Fetching article: %s", api_url)
        data = self._get_json(api_url)
        return self._extract_sentences(data)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _extract_sentences(self, data: dict) -> List[str]:
        title = data.get("title", "unknown")
        extract: str = data.get("extract", "")
        logger.info("Article: '%s' (%d chars)", title, len(extract))
        return self._split_sentences(extract)

    def _get_json(self, url: str) -> dict:
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.error("Wikipedia API request failed [%s]: %s", url, exc)
            raise

    @staticmethod
    def _extract_title(url: str) -> str:
        """
        'https://en.wikipedia.org/wiki/Python_(programming_language)'
        → 'Python_(programming_language)'
        """
        path = urlparse(url).path          # /wiki/Python_(programming_language)
        title = path.split("/wiki/")[-1]   # Python_(programming_language)
        return unquote(title)              # URL encoding'i çöz

    @staticmethod
    def _extract_language(url: str) -> str:
        """'https://tr.wikipedia.org/...' → 'tr'"""
        hostname = urlparse(url).hostname or "en.wikipedia.org"
        return hostname.split(".")[0]

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        sentences = _SENTENCE_SPLITTER.split(text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.headers.update(
            {"User-Agent": "kafka-word-processor/1.0"}
        )
        return session