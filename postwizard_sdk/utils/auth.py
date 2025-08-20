"""
Authentication Utilities

This module contains functions to handle authentication for the PostWizard API.

Functions:
- get_token() -> Optional[PostWizardAPIToken]: Retrieve the PostWizard API token from the secrets vault.
- basic_auth_flow() -> int: Handles basic authentication flow for the PostWizard API.
- bearer_auth_flow() -> Dict[str, str]: Return the bearer token for subsequent requests to the PostWizard API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
from typing import Dict, Union, Optional

# Third-party imports
import requests
from huggingface_hub import get_token
from requests.auth import HTTPBasicAuth

# Local imports
from postwizard_sdk.builders.api_url_builder import APIUrlBuilder
from core.controllers.secrets_controller import SecretHandler
from core.models.secret_model import SecretType, PostWizardAPILogin, PostWizardAPIToken


class PostWizardAuth:
    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def get_token() -> Optional[PostWizardAPIToken]:
        secret_handler = SecretHandler()
        api_secrets: PostWizardAPIToken = secret_handler.get_secret(
            SecretType.PWAPI_TOKEN, cascade_secret_type=True
        )
        return api_secrets

    @staticmethod
    def basic_auth_flow() -> int:
        secret_handler = SecretHandler()
        if PostWizardAuth.get_token():
            secret_handler.delete_secret(
                SecretType.PWAPI_TOKEN, cascade_secret_type=True
            )
        auth_addr = APIUrlBuilder().login()
        api_secrets: PostWizardAPILogin = secret_handler.get_secret(
            SecretType.PWAPI_PASSWORD, cascade_secret_type=True
        )
        basic_auth = HTTPBasicAuth(api_secrets.api_user, api_secrets.api_secret)
        response_obj = requests.get(auth_addr.build(), auth=basic_auth)
        if response_obj.status_code == requests.codes.ok:
            secret_handler.store_secret(
                SecretType.PWAPI_TOKEN,
                api_secrets.api_user,
                response_obj.json()["access_token"],
                cascade_secret_type=True,
            )
            os.environ[SecretType.PWAPI_TOKEN.value] = "yes"
        return response_obj.status_code

    @staticmethod
    def bearer_auth_flow() -> Dict[str, str]:
        token: Union[PostWizardAPIToken, str] = ""
        if os.environ.get(SecretType.PWAPI_TOKEN.value):
            token = PostWizardAuth.get_token()
        else:
            if PostWizardAuth.basic_auth_flow() == requests.codes.ok:
                token = PostWizardAuth.get_token()
        return {"Authorization": "Bearer {}".format(token.access_token)}
