# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Exceptions for the core package

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
import platform


class NoSuitableArgument(Exception):
    """
    Used by functions that depend on CLI parameters.
    Raise if the expected parameters are not provided by the user.
    """

    def __init__(self, package: str, file: str):
        self.file = (lambda f: os.path.basename(f).split(".")[0])(file)
        self.package = package
        super().__init__(f"Try: python3 -m {self.package}.{self.file} --help")


class InvalidInput(Exception):
    """
    Used by functions that depend on user input.
    Raise if the expected values are not provided via user input.
    """

    def __init__(self):
        self.message = "The input or database you have provided is not valid. Double check it and re-run."
        self.help = "Did you check if all your partners in workflows_config.ini have a corresponding database?"
        super().__init__(f"{self.message}\n{self.help}")


class UnsupportedParameter(Exception):
    """
    Handle instances where the user or controlling function provides a value that the function
    does not support. Typically used in lieu of ValueError.
    """

    def __init__(self, param: str):
        self.param = param
        self.message = f"Unsupported parameter {param}. Try again."
        super().__init__(self.message)


class UnavailableLoggingDirectory(Exception):
    """
    Notifies the user that the logging directory is not accessible.
    """

    def __init__(self, logging_dirname: str):
        self.message = f"Logging directory {logging_dirname} cannot be created nor accessed. Check the workflows_config.ini file again!\n"
        self.help = (
            "Just in case, only add the directory name. The application will detect it."
        )
        super().__init__(self.message + self.help)


class UnsupportedPlatform(Exception):
    """
    Alert the user when a feature can't be completed due to a platform incompatibility.
    """

    def __init__(self, reason: str = "", /):
        self.reason = reason
        self.message = f"Unsupported platform: {platform.platform()} {self.reason}"
        super().__init__(self.message)


class InvalidOperationMode(Exception):
    """
    Exception raised for invalid operation mode in implementation-defined literals.
    """

    def __init__(self, operation: str = "", available_actions: list[str] = []):
        self.operation = operation
        self.message = "Invalid operation mode: {}. Available actions: {}".format(
            operation, ", ".join(available_actions)
        )
        super().__init__(self.message)


class UnsupportedConfigArgument(Exception):
    """
    Exception raised for invalid configuration arguments in configuration validation logic.
    """

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)
