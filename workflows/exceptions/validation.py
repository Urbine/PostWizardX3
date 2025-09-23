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
