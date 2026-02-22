"""Unit tests for WordFilter."""
import pytest
from src.processors.word_filter import WordFilter


@pytest.fixture
def f5():
    return WordFilter(min_length=5)


class TestFilterSentence:
    def test_keeps_long_words(self, f5):
        result = f5.filter_sentence("Hello world this is amazing")
        assert "hello" in result
        assert "world" in result
        assert "amazing" in result

    def test_removes_short_words(self, f5):
        result = f5.filter_sentence("I am a cat")
        assert result == []

    def test_removes_punctuation(self, f5):
        result = f5.filter_sentence("Hello, world! Great.")
        assert "hello" in result
        assert "world" in result
        assert "great" in result

    def test_lowercases_output(self, f5):
        result = f5.filter_sentence("PYTHON Kafka STREAM")
        assert "python" in result
        assert "kafka" in result
        assert "stream" in result

    def test_numbers_excluded(self, f5):
        result = f5.filter_sentence("Python 3 is amazing")
        # "3" is a digit, not matched by letter pattern
        assert all(c.isalpha() for word in result for c in word)

    def test_empty_string(self, f5):
        assert f5.filter_sentence("") == []

    def test_custom_min_length(self):
        wf = WordFilter(min_length=3)
        result = wf.filter_sentence("cat dog elephant")
        assert "cat" in result
        assert "dog" in result
        assert "elephant" in result

    def test_exactly_min_length_included(self, f5):
        # "world" is exactly 5 characters
        result = f5.filter_sentence("world")
        assert "world" in result

    def test_one_below_min_length_excluded(self, f5):
        # "word" is 4 characters – below min_length of 5
        result = f5.filter_sentence("word")
        assert result == []


class TestFilterSentences:
    def test_flat_list_returned(self, f5):
        sentences = ["Hello world", "Python Kafka stream"]
        result = f5.filter_sentences(sentences)
        assert isinstance(result, list)
        assert "hello" in result
        assert "python" in result

    def test_empty_input(self, f5):
        assert f5.filter_sentences([]) == []


class TestConstructor:
    def test_invalid_min_length_raises(self):
        with pytest.raises(ValueError):
            WordFilter(min_length=0)
