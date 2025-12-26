# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
SecretHandler module for managing secrets and authentication.

This module provides the SecretHandler class, which centralizes logic for secret management,
authentication, and integration with various controllers and secret factories in PostWizard.
It benefits from implementations of the ``UniversalSecretController`` interface for controller discovery and operation handling.
"""

from typing import Optional, Literal, Generic, TypeVar, Union, List

# Local imports
from core.controllers.interfaces import UniversalSecretController
from core.secrets.secrets_factory import secrets_factory
from core.models.secret_model import SecretType
from core.utils.decorators import singleton
from core.exceptions.util_exceptions import InvalidOperationMode

# Imported for controller discovery
from core.controllers.auth import *  # noqa: F403

T = TypeVar("T")


@singleton
class SecretHandler(Generic[T]):
    """
    A class for handling secrets and authentication.

    This class provides a unified interface for storing, retrieving, updating, and deleting secrets.
    It allows for easy integration with different authentication and secret management controller classes.
    """

    def __init__(self):
        self.__auth_controller_instances: List[UniversalSecretController] = [
            cls(secrets_factory()) for cls in UniversalSecretController.__subclasses__()
        ]

    def controller_discovery(
        self, secret_type: SecretType
    ) -> Optional[UniversalSecretController]:
        """
        Discover and return the UniversalSecretController instance for a given secret type.

        :param secret_type: ``SecretType`` -> The type of secret to retrieve.
        :return: ``Optional[UniversalSecretController]`` ->
                The UniversalSecretController instance for the given secret type, or None if not found.
        """
        for auth_controller in self.__auth_controller_instances:
            if secret_type in auth_controller.supported_secret_types:
                return auth_controller
        return None

    def handle_secret(
        self,
        secret_type: SecretType,
        action: Literal["put", "get", "update", "delete"],
        /,
        *args,
        cascade_secret_type: bool = False,
    ) -> Optional[T | List[T] | bool]:
        """
        Handle a secret based on its type and operation mode.

        :param secret_type: ``SecretType`` -> The type of secret to handle.
        :param action: ``Literal["put", "get", "update", "delete"]`` -> The operation mode to perform.
        :param args: ``tuple`` -> Additional arguments for the operation.
        :param cascade_secret_type: ``bool`` -> Whether to cascade the secret type to the controller.
        :return: ``Optional[T | List[T] | bool]`` -> The result of the operation, or None if not found.
        """
        auth_controller = self.controller_discovery(secret_type)
        output_completion: Optional[Union[T, bool, List[T]]] = None
        real_args = [*args]
        # Some controllers select a method that directly depend on SecretType.
        if cascade_secret_type:
            real_args.insert(0, secret_type)
        match action:
            case "put":
                output_completion = auth_controller.store_secrets(*real_args)
            case "get":
                output_completion = auth_controller.get_secrets(*real_args)
            case "update":
                output_completion = auth_controller.update_secrets(*real_args)
            case "delete":
                output_completion = auth_controller.delete_secrets(*real_args)
            case _:
                raise InvalidOperationMode(
                    operation=action,
                    available_actions=["put", "get", "update", "delete"],
                )

        return output_completion

    def store_secret(
        self, secret_type: SecretType, /, *args, cascade_secret_type: bool = False
    ):
        """
        Store a secret based on its type.

        :param secret_type: ``SecretType`` -> The type of secret to store.
        :param args: ``tuple`` -> Additional arguments for the operation.
        :param cascade_secret_type: ``bool`` -> Whether to cascade the secret type to the controller instance method.
        :return: ``bool`` -> True if the secret was stored successfully, False otherwise.
        """
        return self.handle_secret(
            secret_type, "put", *args, cascade_secret_type=cascade_secret_type
        )

    def get_secret(
        self, secret_type: SecretType, /, *args, cascade_secret_type: bool = False
    ):
        """
        Get a secret based on its type.

        :param secret_type: ``SecretType`` -> The type of secret to retrieve.
        :param args: ``tuple`` -> Additional arguments for the operation.
        :param cascade_secret_type: ``bool`` -> Whether to cascade the secret type to the controller instance method.
        :return: ``Optional[T | List[T]]`` -> The retrieved secret, or None if not found.
        """
        return self.handle_secret(
            secret_type, "get", *args, cascade_secret_type=cascade_secret_type
        )

    def update_secret(
        self, secret_type: SecretType, /, *args, cascade_secret_type: bool = False
    ):
        """
        Update a secret based on its type.

        :param secret_type: ``SecretType`` -> The type of secret to update.
        :param args: ``tuple`` -> Additional arguments for the operation.
        :param cascade_secret_type: ``bool`` -> Whether to cascade the secret type to the controller instance method.
        :return: ``bool`` -> True if the secret was updated successfully, False otherwise.
        """
        return self.handle_secret(
            secret_type, "update", *args, cascade_secret_type=cascade_secret_type
        )

    def store_probe_secret(
        self, secret_type: SecretType, /, *args, cascade_secret_type: bool = False
    ):
        """
        Store or update a secret based on its type. It assumes that both, the update function and the store function,
        have the same signature. In case that is not the case, it is recommended to use the store_secret and
        update_secret functions separately if you need to verify if the secret exists before storing.

        :param secret_type: ``SecretType`` -> The type of secret to store or update.
        :param args: ``tuple`` -> Additional arguments for the operation.
        :param cascade_secret_type: ``bool`` -> Whether to cascade the secret type to the controller instance method.
        :return: ``bool`` -> True if the secret was stored or updated successfully, False otherwise.
        """
        probe_secrets = self.get_secret(
            secret_type, *args, cascade_secret_type=cascade_secret_type
        )
        if probe_secrets:
            return self.update_secret(
                secret_type, *args, cascade_secret_type=cascade_secret_type
            )
        else:
            return self.store_secret(
                secret_type, *args, cascade_secret_type=cascade_secret_type
            )

    def delete_secret(
        self, secret_type: SecretType, /, *args, cascade_secret_type: bool = False
    ):
        """
        Delete a secret based on its type.

        :param secret_type: ``SecretType`` -> The type of secret to delete.
        :param args: ``tuple`` -> Additional arguments for the operation.
        :param cascade_secret_type: ``bool`` -> Whether to cascade the secret type to the controller instance method.
        :return: ``bool`` -> True if the secret was deleted successfully, False otherwise.
        """
        return self.handle_secret(
            secret_type, "delete", *args, cascade_secret_type=cascade_secret_type
        )


if __name__ == "__main__":
    # This module is not intended to be run as a script.
    # It is designed to be imported and used in other modules.
    raise RuntimeError("This module is not intended to be run as a script.")
