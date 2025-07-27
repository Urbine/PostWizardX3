"""
Universal Controller Interface for managing secrets and authentication.

This module provides an abstract base class that defines a standardized interface
for controllers handling authentication and secrets management across different
service providers. It enforces a consistent API for CRUD operations on secrets.
"""

from abc import ABC, abstractmethod
from typing import Optional, Generic, TypeVar, Union, List, Iterable

from core.secrets.secret_repository import SecretsDBInterface
from core.models.secret_model import SecretType

T = TypeVar("T")


class UniversalSecretController(Generic[T], ABC):
    """
    Abstract base class for authentication and secrets management controllers.

    This class defines a standard interface for CRUD operations on secrets,
    with type safety and clear method contracts. Subclasses must implement
    the abstract methods to provide specific authentication provider functionality.

    Type Parameters:
        T: The type of secret data model this controller manages
    """

    def __init__(
        self, secrets_db: SecretsDBInterface, secret_types: Iterable[SecretType]
    ):
        """
        Initialize the controller with a secrets database interface.

        :param secrets_db: The secrets database interface to use for storage
        """
        self._universal_db: SecretsDBInterface = secrets_db
        self._secret_types: Iterable[SecretType] = secret_types

    @property
    # @abstractmethod
    def supported_secret_types(self) -> Iterable[SecretType]:
        return self._secret_types

    @abstractmethod
    def store_secrets(self, *args) -> bool:
        """
        Store secrets in the database.

        :param args: Variable length argument list containing the secret data to store.
                     The exact parameters depend on the implementation.
        :returns: True if storage was successful, False otherwise
        """
        pass

    @abstractmethod
    def update_secrets(self, *args) -> bool:
        """
        Update existing secrets in the database.

        :param args: Variable length argument list containing the updated secret data.
                     The exact parameters depend on the implementation.
        :returns: True if update was successful, False otherwise
        """
        pass

    @abstractmethod
    def get_secrets(self, *args) -> Optional[Union[T, List[T]]]:
        """
        Retrieve secrets from the database.

        :returns: The retrieved secret(s) or None if not found.
                 Can return either a single item of type T or a list of T.
        """
        pass

    @abstractmethod
    def delete_secrets(self, *args) -> bool:
        """
        Delete secrets from the database.

        :param args: Variable length argument list containing the secret identifier(s) to be deleted.
                      The exact parameters depend on the implementation.
        :returns: True if deletion was successful, False otherwise
        """
        pass
