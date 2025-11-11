"""
Validation Exceptions

This module contains custom exceptions for validation purposes.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


class IncompatibleLinkException(Exception):
    """
    Exception raised when an invalid link structure is detected and
    a change to the link workers might be needed in the infrastructure.

    """

    def __init__(self, link: str):
        self.link = link
        self.message = f"Foreign link: {self.link} detected"
        self.advice = (
            "Please check compatibility with workers in place and update if needed."
        )
        super().__init__(f"{self.message}\n{self.advice}")


class InvalidPostQuantityException(Exception):
    """
    Exception raised when an invalid post quantity is detected and
    the user has not added a post quantity before running the bot in headless mode.
    """

    def __init__(self, post_quantity: int):
        self.post_quantity = post_quantity
        self.message = f"Invalid post quantity: {self.post_quantity}"
        self.advice = "Make sure to add the post quantity before running the bot in headless mode."
        super().__init__(f"{self.message}\n{self.advice}")


class DataSourceUpdateError(Exception):
    """
    Exception raised when an error occurs during an update process
    that involves data sources in sequential mode.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
