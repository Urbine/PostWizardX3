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

from requests import Response


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
        self.message = (
            "The input you have provided is not valid. Double check it and re-run."
        )
        super().__init__(self.message)


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
        self.message = f"Double check your True/False (boolean) values in configuration options."
        super().__init__(self.message)


class RefreshTokenError(Exception):
    """
    Handle X API refresh token errors.
    """

    def __init__(self, res: Response):
        self.status = res.status_code
        self.reason = res.reason
        self.help = "Regenerate the tokens and try again: python3 -m integrations.x_api --headless"
        self.message = f"Status code: {self.status} \nReason: {self.reason}"
        super().__init__(f"{self.message} \n{self.help}")


class AccessTokenRetrivalError(Exception):
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
        self.message = """WP JSON HotSync validation failed.
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
