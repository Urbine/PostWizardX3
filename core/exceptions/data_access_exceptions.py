# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Data Access exceptions


Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


class InvalidDB(Exception):
    """
    Catches SQLite3's OperationalError in order to give a useful error message to
    the user.
    """

    def __init__(self, db_path_used: str):
        self.message = "Invalid or absent database."
        self.help = (
            "Make sure you have the database required by the module you're running."
        )
        self.path = f"Database path passed: {db_path_used}"
        super().__init__(f"{self.message} {self.help} {self.path}")


class InvalidSQLConfig(Exception):
    """
    Exception raised for invalid SQL configuration.
    This exception is used to indicate when an invalid SQL query configuration
    is detected for a specific partner.
    """

    def __init__(self, partner: str = ""):
        self.message = (
            f"Invalid SQL Query found in configuration for partner {partner}.\n"
        )
        self.help = "Make sure you have the correct SQL query for the partner you plan to work with in this session."
        super().__init__(f"{self.message} {self.help}")


class UnableToConnectError(Exception):
    """
    Notifies the user if there is no internet connection.
    """

    def __init__(self):
        super().__init__("Unable to connect. Check your internet connection!")
