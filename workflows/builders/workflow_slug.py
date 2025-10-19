"""
WorkflowSlug builder class

WorkflowSlug extends the ``WordFilter`` class and provides additional functionality
for building slugs, a common task in content management workflows in this package.

It can remove stopwords from the input text and filter out non-alphanumeric characters and custom words.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self, Iterable, Optional

from workflows.interfaces.word_filter import WordFilter


class WorkflowSlugBuilder(WordFilter):
    """
    WorkflowSlug provides enhanced slug generation for content management workflows.

    Extends the ``WordFilter`` class with specialized features for content management, including: \n
    - Stopword removal in multiple languages
    - Custom word filtering
    - Domain-specific segment handling (partner, model, title, etc.)

    :param stopword_removal: ``bool``, Default: ``None` -> Whether to remove stopwords from the input text.
    :param stopwords_lang: ``str`` -> The language of the stopwords to remove.
    :param filter_words: ``Optional[Iterable[str]]`` -> A list of words to filter out from the input text.
    :param enforce_unique: ``bool`` -> Whether to enforce unique terms in the slug.
    """

    def __init__(
        self,
        stopword_removal: bool = True,
        stopwords_lang: str = "english",
        filter_words: Optional[Iterable[str]] = None,
        enforce_unique: bool = True,
    ):
        super().__init__(
            delimiter="-",
            filter_words=filter_words,
            stopword_removal=stopword_removal,
            stopwords_lang=stopwords_lang,
            enforce_unique=enforce_unique,
        )

    def __add_segment(self, segment: str) -> Self:
        """
        Adds a segment to the slug.

        :param segment: ``str`` The segment to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        return self.add_word(segment)

    def partner(self, partner: str) -> Self:
        """
        Adds a partner segment to the slug.

        :param partner: ``str`` The partner to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        return self.__add_segment(partner)

    def model(self, model: str) -> Self:
        """
        Adds a model segment to the slug.

        :param model: ``str`` The model to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        return self.__add_segment(model)

    def title(self, title: str) -> Self:
        """
        Adds a title segment to the slug.

        :param title: ``str`` The title to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        return self.__add_segment(title)

    def content_type(self, content_type: str) -> Self:
        """
        Adds a content type segment to the slug.

        :param content_type: ``str`` The content type to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        return self.__add_segment(content_type)

    def studio(self, studio: str) -> Self:
        """
        Adds a studio segment to the slug.

        :param studio: ``str`` The studio to add to the slug.
        :return: ``Self`` The current instance of the class for chaining.
        """
        return self.__add_segment(studio)

    def build(self) -> str:
        """
        Builds the slug using the segments added to the slug.
        Delegates building to its parent class.

        :return: ``str`` The built slug.
        """
        return super().build().lower()
