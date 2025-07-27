"""
Custom exceptions are meant to provide a project-specific and behavioural
control of our core functions. It makes sense to include then, so that more
information can be given to users in a non-generic way.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
from pathlib import Path

from requests import Response


class UnableToConnectError(Exception):
    """
    Notifies the user if there is no internet connection.
    """

    def __init__(self):
        super().__init__("Unable to connect. Check your internet connection!")


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


class ConfigFileNotFound(Exception):
    """
    Deal with instances where a configuration file does not exist.
    If this happens, you may want to check the filename or create the configuration
    file according to the needs of the project.

    """

    def __init__(self, filename: str, package: str):
        self.filename = filename
        self.package = package
        self.message = f"Filename {filename} does not exist in package {package}. Create it if you haven't already."
        super().__init__(self.message)


class UnsupportedParameter(Exception):
    """
    Handle instances where the user or controlling function provides a value that the function
    does not support. Typically used in lieu of ValueError.
    """

    def __init__(self, param: str):
        self.param = param
        self.message = f"Unsupported parameter {param}. Try again."
        super().__init__(self.message)


class InvalidConfiguration(Exception):
    """
    Handle configuration errors that may occur on keys dealing with boolean values or
    values that must abide by Python's syntactic rules.
    """

    def __init__(self):
        self.message = (
            "Double check your True/False (boolean) values in configuration options."
        )
        super().__init__(self.message)


class RefreshTokenError(Exception):
    """
    Handle X API refresh token errors.
    """

    def __init__(self, res: Response):
        self.status = res.status_code
        self.reason = res.reason
        self.help = "Regenerate the tokens and try again: python3 -m integrations.x_api --headless"
        self.message = f"Status code: {self.status!r} \nReason: {self.reason!r}"
        super().__init__(f"{self.message} \n{self.help}")


class AccessTokenRetrievalError(Exception):
    """
    Notifies the user when the authorization flow is unsuccessful.
    """

    def __init__(self, res: Response):
        self.status = res.status_code
        self.reason = res.reason
        self.message = (
            f"No Access Token found: \nStatus: {self.status} \nReason: {self.reason}"
        )
        super().__init__(self.message)


class HotFileSyncIntegrityError(Exception):
    """
    Notifies the user about failures in the HotFileSync process.
    Changes will not touch the wp_posts.json file if the config cannot be validated.
    In this case, you may want to investigate what went wrong, but it is way easier to
    rebuild the WordPress post caching and its config file.
    """

    def __init__(self):
        self.message = """WP JSON HotSync failed validation!
                          Maybe you have to rebuild your WordPress cache and its config.
                          Run (in project root): python3 -m integrations.wordpress_api --posts --yoast"""
        super().__init__(self.message)


class AssetsNotFoundError(Exception):
    """
    Notifies the user in case there are no assets in the asset config file.
    However, if there is no config file, exception ``ConfigFileNotFound`` may occur first.
    """

    def __init__(self):
        self.message = """No assets found in config file. 
                          Make sure you add your assets to the corresponding file before launching this application."""
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


class NoFieldsException(Exception):
    """
    Notifies the user when no fields have been provided or all fields were excluded
    via cli flags.
    """

    def __init__(self):
        self.message = (
            "Unable to generate schema and/or request URL due to insufficient options."
        )
        self.help = "Try to run the module with the --help flag to know more. This module requires at least one field."
        super().__init__(f"{self.message}\n{self.help}")


class InvalidDB(Exception):
    """
    Catches SQLite3's OperationalError in order to give a useful error message to
    the user.
    """

    def __init__(self):
        self.message = "Invalid or absent database."
        self.help = (
            "Make sure you have the database required by the module you're running."
        )
        super().__init__(f"{self.message} {self.help}")


class BraveAPIValidationError(Exception):
    """
    Communicate with users about query parameter validation errors in the Brave API wrapper.
    """

    def __init__(self, json_response):
        self.message = "Please verify the maximums, flags and defaults of the vertical you are working with."
        self.help = json_response["error"]["msg"]
        super().__init__(f"{self.message}\n{self.help}")


class BraveAPIInvalidCountryCode(Exception):
    """
    Communicate with users about an invalid country code provided to the Brave API wrapper.
    """

    def __init__(self, code):
        self.message = f'"{code}" is an invalid Country Code!'
        self.help = "Refer to https://api-dashboard.search.brave.com/app/documentation/web-search/codes"
        super().__init__(
            f"{self.message}\n{self.help} for more information on accepted codes"
        )


class BraveAPIInvalidLanguageCode(Exception):
    """
    Communicate with users about an invalid language code provided to the the Brave API wrapper.
    """

    def __init__(self, code):
        self.message = f'"{code}" is an invalid Language/Market Code!'
        self.help = "Refer to https://api-dashboard.search.brave.com/app/documentation/web-search/codes"
        super().__init__(
            f"{self.message}\n{self.help} for more information on accepted codes"
        )


class MissingCacheError(Exception):
    """
    Alert users when the application is trying to update a cache file that does not exist.
    """

    def __init__(self, filename):
        self.message = f'Cache "{filename}" does not exist!'
        self.help = "Rebuild your WordPress cache."
        super().__init__(
            f"{self.message}\n{self.help} Run (in project root): python3 -m integrations.wordpress_api --posts --yoast"
        )


class ClientInfoSecretsNotFound(Exception):
    """
    Appear when the main secrets file is missing or its secrets are invalid and cannot be parsed by
    the Configuration Manager module.
    """

    def __init__(self, path: str | Path):
        self.path = f"Client info secrets not found at `{path}`\n"
        self.reason = "Make sure you have the client_info.ini file in your config directory and all its entries populated.\n"
        self.advise = "Tip: If you are just using a subset of secrets in your use case, you can add dummy values."
        super().__init__(self.path + self.reason + self.advise)


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


class InvalidAIConfig(Exception):
    """
    The InvalidAIConfig class represents an error object used when there is a misconfiguration or lack of AI system's parameters or settings.
    """

    def __init__(self, message: str = ""):
        self.message = message
        self.help = "Double check your AI configuration under the `general_config` section in the workflows_config.ini file."
        super().__init__(f"{self.message}\n{self.help}")
