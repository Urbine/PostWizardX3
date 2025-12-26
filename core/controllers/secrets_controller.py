# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Secrets Controller Module
This module provides functions for updating and storing secrets in the secret vault.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging

import gradio as gr

from core.utils.secret_handler import SecretHandler
from core.models.secret_model import SecretType

SECRET_HANDLER = SecretHandler()

# ------ Local utility functions ------


def info_store_secret(store_update_output: bool) -> None:
    """
    This function displays a success or error message based on the value of store_update_output.

    :param store_update_output: A boolean value indicating whether the secrets were successfully stored or not.
    :return: None
    """
    if store_update_output:
        logging.info("Secrets have been stored")
        gr.Success(message="Your secrets have been updated")
    else:
        logging.error("Failed to store secrets")
        gr.Error(
            message="Failed to store your secrets. Check that all information has been supplied"
        )
    return None


def info_delete_secret(delete_output: bool, toggle_notification: bool = False) -> None:
    """
    This function displays a success or error message based on the value of delete_output.

    :param delete_output: A boolean value indicating whether the secrets were successfully deleted or not.
    :param toggle_notification: A boolean value indicating whether to toggle the notification or not.
    :return: None
    """
    if toggle_notification:
        if delete_output:
            gr.Success(message="Your secrets have been deleted")
        else:
            gr.Error(message="Failed to delete your platform secrets.")
    return None


def store_secrets(
    secret_type: SecretType,
    /,
    *args,
    cascade_secret_type: bool = False,
):
    """
    This function stores secrets in the secret handler.

    :param secret_type: The type of secret to store.
    :param args: Additional arguments to pass to the secret handler.
    :param cascade_secret_type: Whether to cascade the secret type to the secret handler.
    :return: A boolean value indicating whether the secrets were successfully stored or not.
    """
    return info_store_secret(
        SECRET_HANDLER.store_secret(
            secret_type, *args, cascade_secret_type=cascade_secret_type
        )
    )


# ------ Specialised functions ------


def update_store_x_secret(secret_type: SecretType, /, *args):
    """
    This function updates and stores secrets in the secret handler.

    :param secret_type: The type of secret to update and store.
    :param args: Additional arguments to pass to the secret handler.
    :return: A boolean value indicating whether the secrets were successfully updated and stored or not.
    """
    secrets = SECRET_HANDLER.get_secret(secret_type, cascade_secret_type=True)
    if secrets:
        SECRET_HANDLER.delete_secret(secret_type, cascade_secret_type=True)
    return store_secrets(secret_type, *args, cascade_secret_type=True)


def wp_remove_secrets(*args, toggle_notification: bool = True) -> None:
    """
    This function removes the WordPress app password from the secret vault.

    :param toggle_notification: A boolean value indicating whether to toggle the notification or not.
    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.WP_APP_PASSWORD, *args),
        toggle_notification=toggle_notification,
    )


def wp_update_secrets(*args) -> None:
    """
    This function updates and stores secrets in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    secret_type = SecretType.WP_APP_PASSWORD
    secrets = SECRET_HANDLER.get_secret(secret_type)
    if secrets:
        wp_remove_secrets(secrets[0].hostname, toggle_notification=False)
    return store_secrets(secret_type, *args)


def google_remove_secrets(toggle_notification: bool = True) -> None:
    """
    This function removes the Google Search API key from the secret vault.

    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.GOOGLE_API_KEY),
        toggle_notification=toggle_notification,
    )


def google_update_secrets(*args) -> None:
    """
    This function updates and stores the Google Search API key in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    secret_type = SecretType.GOOGLE_API_KEY
    secrets = SECRET_HANDLER.get_secret(secret_type)
    if secrets:
        google_remove_secrets(toggle_notification=False)
    return store_secrets(secret_type, *args)


def brave_remove_secrets(toggle_notification: bool = True) -> None:
    """
    This function removes the Brave Search API key from the secret vault.

    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.BRAVE_API_KEY),
        toggle_notification=toggle_notification,
    )


def brave_update_secrets(*args) -> None:
    """
    This function updates and stores the Brave Search API key in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    secret_type = SecretType.BRAVE_API_KEY
    secrets = SECRET_HANDLER.get_secret(secret_type)
    if secrets:
        brave_remove_secrets(toggle_notification=False)
    return store_secrets(secret_type, *args)


def telegram_remove_secrets(*args, toggle_notification: bool = True) -> None:
    """
    This function removes the Telegram access token from the secret vault.

    :param toggle_notification: A boolean value indicating whether to toggle the notification or not.
    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.TELEGRAM_ACCESS_TOKEN, *args),
        toggle_notification=toggle_notification,
    )


def telegram_update_secrets(*args) -> None:
    """
    This function updates and stores secrets in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    secret_type = SecretType.TELEGRAM_ACCESS_TOKEN
    secrets = SECRET_HANDLER.get_secret(secret_type)
    if secrets:
        telegram_remove_secrets(secrets[0].chat_id)
    return store_secrets(secret_type, *args)


def x_remove_api_secrets(toggle_notification: bool = True) -> None:
    """
    This function removes X Platform API secrets from the secret vault.

    :param toggle_notification: A boolean value indicating whether to toggle the notification or not.
    :return: ``None``
    """
    info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.X_API_KEY, cascade_secret_type=True),
        toggle_notification=toggle_notification,
    )
    SECRET_HANDLER.delete_secret(SecretType.X_API_SECRET, cascade_secret_type=True)
    return None


def x_update_api_secrets(*args) -> None:
    """
    This function deletes and stores X Platform API secrets in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    return update_store_x_secret(SecretType.X_API_KEY, *args)


def x_remove_credentials(toggle_notification: bool = True) -> None:
    """
    This function removes the X platform password and associated credentials from the secret vault.

    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.X_PASSWORD, cascade_secret_type=True),
        toggle_notification=toggle_notification,
    )


def x_update_credentials(*args) -> None:
    """
    This function updates and stores the X platform password and credentials in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    return update_store_x_secret(SecretType.X_PASSWORD, *args)


def x_client_update_secrets(*args) -> None:
    """
    This function updates and stores secrets in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    return update_store_x_secret(SecretType.X_CLIENT_SECRET, *args)


def x_client_remove_secrets(toggle_notification: bool = True) -> None:
    """
    This function removes the X Platform client secret from the secret vault.

    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(
            SecretType.X_CLIENT_SECRET, cascade_secret_type=True
        ),
        toggle_notification=toggle_notification,
    )


def monger_cash_remove_credentials(toggle_notification=True) -> None:
    """
    This function removes the MongerCash affiliate program credentials from the secret vault.

    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(SecretType.MONGERCASH_PASSWORD),
        toggle_notification=toggle_notification,
    )


def monger_cash_update_credentials(*args) -> None:
    """
    This function updates and stores the MongerCash affiliate program credentials in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    secrets = SECRET_HANDLER.get_secret(SecretType.MONGERCASH_PASSWORD)
    if secrets:
        monger_cash_remove_credentials(toggle_notification=False)
    return store_secrets(SecretType.MONGERCASH_PASSWORD, *args)


def pw_api_remove_credentials(toggle_notification: bool = True) -> None:
    """
    This function removes the PostWizard API credentials from the secret vault.

    :param toggle_notification: A boolean value indicating whether to toggle the notification or not.
    :return: ``None``
    """
    return info_delete_secret(
        SECRET_HANDLER.delete_secret(
            SecretType.PWAPI_PASSWORD, cascade_secret_type=True
        ),
        toggle_notification=toggle_notification,
    )


def pw_api_update_credentials(*args) -> None:
    """
    This function updates and stores the PostWizard API credentials in the secret vault.

    :param args: Additional arguments to pass to the secret handler.
    :return: ``None``
    """
    secrets = SECRET_HANDLER.get_secret(
        SecretType.PWAPI_PASSWORD, cascade_secret_type=True
    )
    if secrets:
        pw_api_remove_credentials(toggle_notification=False)
    return store_secrets(SecretType.PWAPI_PASSWORD, *args, cascade_secret_type=True)


if __name__ == "__main__":
    # This module is not intended to be run as a script.
    # It is designed to be imported and used in other modules.
    raise RuntimeError("This module is not intended to be run as a script.")
