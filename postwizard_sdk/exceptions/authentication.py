# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Authentication Exceptions

This module contains custom exceptions for authentication purposes.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""

    def __init__(self, message: str, status: int):
        self.message = message
        self.status = status
        super().__init__(f"{self.message}\n Status: {self.status}")
