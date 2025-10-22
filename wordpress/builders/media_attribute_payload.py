"""
MediaAttributePayload builder class

This class is a builder for a simple WordPress media attribute payload.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self

from wordpress.interfaces import SimplePayloadBuilder
from wordpress.models import ImagePayloadItem


class MediaAttributePayload(SimplePayloadBuilder):
    """
    MediaAttributePayload class

    Builder class for a simple WordPress media attribute payload.
    """

    def __init__(self):
        super().__init__()

    def alt_text(self, alt_text: str) -> Self:
        """
        Add an alt text to the payload.

        :param alt_text:  ``str`` -> The alt text to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(ImagePayloadItem.ALT_TEXT, alt_text)
        return self

    def caption(self, caption: str) -> Self:
        """
        Add a caption to the payload.

        :param caption:  ``str`` -> The caption to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(ImagePayloadItem.CAPTION, caption)
        return self

    def description(self, description: str) -> Self:
        """
        Add a description to the payload.

        :param description:  ``str`` -> The description to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(ImagePayloadItem.DESCRIPTION, description)
        return self
