"""
Exceptions related to configuration management in the project.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from pathlib import Path


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


class SectionsNotFoundError(Exception):
    """
    Notifies the user in case there are no assets in the asset config file.
    However, if there is no config file, exception ``ConfigFileNotFound`` may occur first.
    """

    def __init__(self):
        self.message = """No assets found in config file. 
                          Make sure you add your assets to the corresponding file before launching this application."""
        super().__init__(self.message)


class ClientSecretsNotFound(Exception):
    """
    Raised when the main secrets file is missing or contains invalid entries that cannot be parsed by
    the Configuration Manager module.
    """

    def __init__(self, path: str | Path):
        self.path = f"Client secrets file not found at `{path}`.\n"
        self.reason = "Ensure that your secrets are available and correctly configured in the secret_manager.\n"
        self.advice = "Tip: If you only need a subset of secrets, you may use placeholder values for unused fields."
        super().__init__(self.path + self.reason + self.advice)


class InvalidAIConfig(Exception):
    """
    The InvalidAIConfig class represents an error object used when there is a misconfiguration or lack of AI system's parameters or settings.
    """

    def __init__(self, message: str = ""):
        self.message = message
        self.help = "Double check your AI configuration under the `general_config` section in the workflows_config.ini file."
        super().__init__(f"{self.message}\n{self.help}")
