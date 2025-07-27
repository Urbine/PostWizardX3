"""
Exception classes for the integration modules

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from requests import Response


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
    Notifies the user when the X authorization flow is unsuccessful.
    """

    def __init__(self, res: Response):
        self.status = res.status_code
        self.reason = res.reason
        self.message = (
            f"No Access Token found: \nStatus: {self.status} \nReason: {self.reason}"
        )
        super().__init__(self.message)


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
