# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Naive Slug Builder

This module defines the NaiveSlugBuilder base class, which implements a simple slug builder for content posts.

This class is not intended to be used as a standalone class, but rather as an interface for other classes
that need to build slugs and require their own special building logic and methods.
It can also be used by short methods that perform slug building tasks.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self, Iterable, Optional
import regex as re


class NaiveSlugBuilder:
    """
    A class to build slugs for content posts.

    :param delimiter: ``str`` The delimiter to use for the slug.
    :param filter_pattern: ``str`` The regex pattern to allow for in slug creation.
    :param unique_terms: ``bool`` Whether to enforce unique terms in the slug.
    """

    def __init__(
        self,
        delimiter: str = "-",
        filter_pattern: str = r"[^a-z0-9]+",
        unique_terms: bool = True,
    ):
        self._buffer = []
        self._delim = delimiter
        self._filter_pattern = filter_pattern
        self._unique_terms = unique_terms

    def _add_keyword(self, kw_name: str) -> Self:
        """
        Adds a keyword to the buffer list.
        Whether to add the keyword or not depends on the `unique_terms` parameter.
        If `unique_terms` is set to `True`, the keyword will be added only if it is
        not already in the buffer list.

        :param kw_name: ``str`` The keyword to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        if kw_name:
            for kw in re.split(self._filter_pattern, kw_name):
                if kw:
                    if self._unique_terms:
                        if kw not in self._buffer:
                            self._buffer.append(kw)
                    else:
                        self._buffer.append(kw)
        return self

    def _add_keywords(self, kw_list: Iterable[str]) -> Self:
        """
        Adds a list of keywords to the slug.

        :param kw_list: ``Iterable[str]`` The list of keywords to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        if kw_list:
            for kw in kw_list:
                self._add_keyword(kw)

        return self

    def peek(self) -> str:
        """
        Returns a preview of what the built slug would look like.
        Useful if the user needs to display the slug before consumption

        :return: ``str`` The prepared slug.
        """
        if self._unique_terms:
            return self._delim.join(list(dict.fromkeys(self._buffer)))

        return self._delim.join(self._buffer)

    def build(self) -> Optional[str]:
        """
        Returns the constructed slug and cleans the builder for reuse.
        Consumers must call this method when the slug is done and no more
        appending is needed.

        :return: ``str`` The final slug.
        """
        try:
            last_peek = self.peek()
            return last_peek.strip(self._delim) if last_peek else None
        finally:
            self._buffer.clear()
