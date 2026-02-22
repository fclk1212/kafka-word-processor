"""Unit tests for WikipediaFetcher using mocked HTTP responses."""
import pytest
import responses as resp_mock

from src.fetchers.wikipedia import WikipediaFetcher


SAMPLE_EXTRACT = (
    "Python is a high-level programming language. "
    "It was created by Guido van Rossum in 1991. "
    "Python emphasizes code readability."
)

MOCK_RESPONSE = {
    "title": "Python (programming language)",
    "extract": SAMPLE_EXTRACT,
    "lang": "en",
}


@pytest.fixture
def fetcher():
    return WikipediaFetcher(language="en")


@resp_mock.activate
def test_fetch_sentences_returns_list(fetcher):
    resp_mock.add(
        resp_mock.GET,
        "https://en.wikipedia.org/api/rest_v1/page/random/summary",
        json=MOCK_RESPONSE,
        status=200,
    )
    sentences = fetcher.fetch_sentences()
    assert isinstance(sentences, list)
    assert len(sentences) == 3


@resp_mock.activate
def test_sentences_content(fetcher):
    resp_mock.add(
        resp_mock.GET,
        "https://en.wikipedia.org/api/rest_v1/page/random/summary",
        json=MOCK_RESPONSE,
        status=200,
    )
    sentences = fetcher.fetch_sentences()
    assert any("Python" in s for s in sentences)


@resp_mock.activate
def test_empty_extract_returns_empty_list(fetcher):
    resp_mock.add(
        resp_mock.GET,
        "https://en.wikipedia.org/api/rest_v1/page/random/summary",
        json={"title": "Empty", "extract": ""},
        status=200,
    )
    assert fetcher.fetch_sentences() == []


@resp_mock.activate
def test_http_error_raises(fetcher):
    resp_mock.add(
        resp_mock.GET,
        "https://en.wikipedia.org/api/rest_v1/page/random/summary",
        status=503,
    )
    with pytest.raises(Exception):
        fetcher.fetch_sentences()


def test_different_language_uses_correct_url():
    tr_fetcher = WikipediaFetcher(language="tr")
    assert "tr.wikipedia.org" in tr_fetcher._base_url
