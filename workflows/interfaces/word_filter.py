"""
WordFilter class interface

This module provides a class for filtering words from a string.
WordFilter can be used as a base class or as a standalone class depending on the
requirements of the workflow.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, List, Self
import regex as re

# Third-party imports
from nltk.corpus import stopwords

# Local imports
from workflows.interfaces import NaiveSlugBuilder


class WordFilter(NaiveSlugBuilder):
    """
    WordFilter extends the ``NaiveSlugBuilder`` class and provides additional functionality
    for building slugs, a common task in content management workflows in this package.

    It can remove stopwords from the input text and filter out characters that conform to a pattern and custom words.
    It filters non-alphanumeric characters by default.

    :param delimiter: ``str`` The desired delimiter to use for filtering and splitting the text.
    :param filter_words: ``list[str]`` The list of words to filter out.
    :param stopword_removal: ``bool`` Whether to remove stopwords from the text.
    :param stopwords_lang: ``str`` The language of the stopwords to remove.
    :param enforce_unique: ``bool`` Whether to enforce unique words in the text.
    :param filter_pattern: ``str`` The pattern to use for filtering the text.
    :param normalize: ``bool`` Whether to apply lower case to the text irrespective of the regex pattern.
    """

    def __init__(
        self,
        delimiter: str,
        filter_words: Optional[List[str]] = None,
        stopword_removal: bool = False,
        stopwords_lang: str = "english",
        enforce_unique: bool = False,
        filter_pattern: str = r"[^a-zA-Z0-9]+",
    ):
        super().__init__(
            delimiter=delimiter,
            unique_terms=enforce_unique,
            filter_pattern=filter_pattern,
        )
        self._filter_words = filter_words
        self._stopword_removal = stopword_removal
        self.__stopwords_lang = stopwords_lang

    def _remove_stopwords(self, segment: str) -> List[str]:
        """
        Removes stopwords from the input text.

        :param segment: ``str`` The segment to remove stopwords from.
        :return: ``str`` The segment with stopwords removed.
        """
        stop_words = set(stopwords.words(self.__stopwords_lang))
        if self._filter_words:
            stop_words.update(self._filter_words)

        words = re.split(self._filter_pattern, segment if segment else "")
        filtered_words = [word for word in words if word and word not in stop_words]

        return filtered_words

    def add_word(self, word: str) -> Self:
        """
        Adds a word to the filter.

        :param word: ``str`` The word to add to the filter.
        :return: ``Self`` The filter object.
        """
        if self._stopword_removal:
            cleaned_word = self._remove_stopwords(word)
            return self._add_keywords(cleaned_word)

        return self._add_keyword(word)

    def add_word_list(self, word_list: List[str]) -> Self:
        """
        Adds a list of words to the filter.

        :param word_list: ``list[str]`` The list of words to add to the filter.
        :return: ``Self`` The filter object.
        """
        return self._add_keywords(word_list)

    def filter(self) -> str:
        """
        Returns the filtered words to be consumed as a string.

        :return: ``str`` The filtered text.
        """
        return self.build()

    def split(self) -> List[str]:
        """
        Convenience method that splits the filtered text into a list of words
        using the delimiter specified in the constructor.

        :return: ``list[str]`` The filtered text split into a list of words.
        """
        return self.filter().split(self._delim)
