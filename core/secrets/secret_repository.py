# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Secret repository module

This module provides a database interface for managing secrets in the application by
implementing the SchemaInterface interface in ``core.models.interfaces.schema_interface``.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from re import Pattern
from typing import Optional

# Third-party imports
from cryptography.fernet import Fernet

# Local imports
from core.utils.decorators import singleton
from core.models.interfaces.schema_interface import SchemaInterface
from core.models.secret_model import SecretType
from ..models.file_system import ApplicationPath, ProjectFile


@singleton
class SecretsDBInterface(SchemaInterface):
    @dataclass(frozen=True)
    class SchemaRegEx:
        """
        Immutable dataclass containing compiled RegEx patterns for class methods.
        Each filed represents a column in the database.

        This class is used to safely retrieve data from the database without hardcoding
        the column names in the methods of the SecretsDBInterface class.
        """

        pat_id: Pattern[str] = re.compile(r"id")
        pat_name: Pattern[str] = re.compile(r"name")
        pat_secret_type: Pattern[str] = re.compile(r"(secret_type)")
        pat_secret: Pattern[str] = re.compile(r"(secret$)")
        pat_created: Pattern[str] = re.compile(r"created_at")
        pat_updated: Pattern[str] = re.compile(r"updated_at")
        pat_metadata: Pattern[str] = re.compile(r"metadata")

    def __init__(self, db_path: str | Path, **kwargs):
        """
        Initialises the SecretsDBInterface with a database connection and cursor.

        :param db_path: Path to the database
        :raises ``TypeError``: If the SchemaRegEx class is not defined in the subclass.
        """
        super().__init__(db_path, **kwargs)

        if not os.path.exists(
            KEY_LOCATION := Path(
                ApplicationPath.KEY_DIR.value, ProjectFile.KEY_NAME.value
            )
        ):
            raise FileNotFoundError(f"Key file not found at {KEY_LOCATION}")
        else:
            with open(KEY_LOCATION, "rb") as key:
                self.__key: Fernet = Fernet(key.read())

    def get_id(self) -> Optional[str | int]:
        """
        Retrieve the ID of the secret entry.

        :return: ``Optional[str | int]`` -> The ID of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_id)

    def get_name(self) -> Optional[str | int]:
        """
        Retrieve the name of the secret entry.

        :return: ``Optional[str | int]`` -> The name of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_name)

    def get_secret_type(self) -> Optional[str]:
        """
        Retrieve the type of the secret entry.

        :return: ``Optional[SecretType]`` -> The type of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_secret_type)

    def get_secret(self) -> Optional[bytes]:
        """
        Retrieve the secret value of the secret entry.

        :return: ``Optional[bytes]`` -> The secret value of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_secret)

    def get_created_at(self) -> Optional[str | int]:
        """
        Retrieve the creation timestamp of the secret entry.

        :return: ``Optional[str | int]`` -> The creation timestamp of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_created)

    def get_updated_at(self) -> Optional[str | int]:
        """
        Retrieve the last updated timestamp of the secret entry.

        :return: ``Optional[str | int]`` -> The last updated timestamp of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_updated)

    def get_metadata(self) -> Optional[str | int]:
        """
        Retrieve the metadata associated with the secret entry.

        :return: ``Optional[str | int]`` -> The metadata of the secret entry, or None if not found.
        """
        return self._safe_retrieve_iter(self.SchemaRegEx.pat_metadata)

    def __secret_select(
        self, predicate: str, /, *args
    ) -> list[tuple[str | int]] | bool:
        """
        Selects secret entries from the database based on a predicate.

        :param predicate: ``str`` -> SQL WHERE clause to filter results
        :param args: ``tuple`` -> Arguments to be passed to the SQL query
        :return: ``list[tuple[str | int]]`` | ``bool`` -> List of tuples containing secret entries or False on failure
        """
        return self._safe_select(predicate, args)

    def __secret_update(self, predicate: str, **kwargs) -> bool:
        """
        Updates secret entries in the database based on a predicate.

        :param predicate: ``str`` -> SQL WHERE clause to filter results
        :param args: ``tuple`` -> Arguments to be passed to the SQL query
        :return: ``bool`` -> ``True`` if the update was successful, ``False`` otherwise
        """
        return self._safe_update(predicate, kwargs)

    def __secret_insert(self, *args) -> bool:
        """
        Inserts a new secret entry into the database.

        :param args: ``tuple`` -> Arguments to be passed to the SQL query
        :return: ``bool`` -> True if the insertion was successful, False otherwise
        """
        return self._safe_insert(args)

    def encrypt_secret(self, secret: str) -> bytes:
        """
        Encrypts a secret string using the Fernet symmetric encryption algorithm.
        """
        secret_encode = secret.encode()
        return self.__key.encrypt(secret_encode)

    def decrypt_secret(self, secret: bytes) -> str:
        """
        Decrypts an encrypted secret using the Fernet symmetric encryption algorithm.
        """
        secret_crypt = self.__key.decrypt(secret)
        return secret_crypt.decode()

    def __add_secret(
        self, name: str, secret_type: SecretType, secret: str, metadata: str
    ) -> bool:
        """
        Adds a new secret entry to the database.

        :param name: ``str`` -> The name of the secret entry
        :param secret_type: ``SecretType`` -> The type of the secret entry
        :param secret: ``str`` -> The secret value to be stored
        :param metadata: ``str`` -> Additional metadata associated with the secret entry
        :return: ``bool`` -> ``True`` if the secret was added successfully, ``False`` otherwise
        """
        return self.__secret_insert(
            name, secret_type.value, self.encrypt_secret(secret), metadata
        )

    def __retrieve_secret_entry(self, predicate: str) -> tuple[str | int] | bool:
        """
        Retrieves a secret entry from the database based on a predicate.

        :param predicate: ``str`` -> SQL WHERE clause to filter results
        :return: ``tuple[str | int]`` | ``str`` -> A tuple containing the secret entry or "-1" if not found
        """
        try:
            return self._safe_select_all(predicate, fetch_one=True)
        except TypeError:
            return False

    def retrieve_entry_by_name(self, name: str) -> tuple[str | int] | bool:
        """
        Retrieves a secret entry by its name.

        :param name: ``str`` -> The name of the secret entry to retrieve
        :return: ``tuple[str | int]`` | ``bool`` -> A tuple containing the secret entry or False if not found
        """
        return self.__retrieve_secret_entry(f"name = '{name}'")

    def retrieve_like_entry(
        self, field: str, like_str: str, fetch_one: bool = False
    ) -> tuple[str | int] | bool:
        """
        Retrieves a secret entry from the database based on a predicate.

        :param field: ``str`` -> Field to search for
        :param like_str: ``str`` -> String to search for
        :param fetch_one: ``bool`` -> If True, fetches a single row; otherwise, fetches all matching rows
        :return: ``tuple[str | int]`` | ``bool`` -> A tuple containing the secret entry or False if not found
        """
        return self._safe_retrieve_like_entry(field, like_str, fetch_one=fetch_one)

    def __retrieve_entry_by_id(self, id_: int):
        """
        Retrieves a secret entry by its ID.

        :param id_: ``int`` -> The ID of the secret entry to retrieve
        :return: ``tuple[str | int]`` | ``bool`` -> A tuple containing the secret entry or False if not found
        """
        entry = self.__retrieve_secret_entry(f"id = {id_}")
        return entry

    def retrieve_secret(self, predicate: str) -> Optional[str]:
        """ "
        Retrieves the secret value from a secret entry based on a predicate.

        :param predicate: ``str`` -> SQL WHERE clause to filter results
        :return: ``Optional[str]`` -> The decrypted secret value or None if not found
        """
        try:
            _, *secret_entry = self._safe_select_all(predicate, fetch_one=True)
        except TypeError:
            return None
        return self.decrypt_secret(secret_entry[2])

    def __remove_secret(self, predicate: str) -> bool:
        """
        Removes a secret entry from the database based on a predicate.

        :param predicate: ``str`` -> SQL WHERE clause to filter results
        :return: ``bool`` -> True if the secret was removed successfully, False otherwise
        """
        return self._safe_delete(predicate)

    def remove_secret_by_name(self, name: str) -> bool:
        """
        Removes a secret entry from the database based on its name.

        :param name: ``str`` -> The name of the secret entry to remove
        :return: ``bool`` -> True if the secret was removed successfully, False otherwise
        """
        return self.__remove_secret(f"name = '{name}'")

    def remove_secret_by_type(self, secret_type: SecretType | str) -> bool:
        """
        Removes a secret entry from the database based on its type.
        Accepts either ``SecretType`` or ``str`` as input depending on the context.
        If you are iterating over a data row, you can use the ``get_secret_type`` method to retrieve the type as a string.
        Otherwise, use the ``SecretType`` enum directly.

        :param secret_type: ``SecretType`` or ``str`` -> The type of the secret entry to remove
        :return: ``bool`` -> True if the secret was removed successfully, False otherwise
        """
        return self.__remove_secret(
            f"secret_type = '{secret_type.value if isinstance(secret_type, SecretType) else secret_type}'"
        )

    def __update_secret(
        self, id_by: str, secret_type: SecretType, new_secret: str
    ) -> bool:
        """
        Updates the secret value of a secret entry identified by its name.

        :param id_by: ``str`` -> The name or identified of the secret entry to update
        :param new_secret: ``str`` -> The new secret value to be stored
        :param secret_type: ``SecretType`` -> The type of the secret entry
        :return: ``bool`` -> True if the secret was updated successfully, False otherwise
        """
        predicate = "name = '{}' AND secret_type = '{}'".format(
            id_by, secret_type.value
        )
        return self._safe_update(
            predicate,
            secret_type=secret_type.value,
            secret=self.encrypt_secret(new_secret),
        )

    def __available_secrets(self) -> list[tuple[str | int]]:
        """
        Retrieves all available secrets from the database.

        :return: ``list[tuple[str | int]]`` -> A list of tuples containing secret entries
        """
        secrets = self._safe_select("id", "name", "secret_type", "secret", "metadata")
        return secrets

    def get_entries_by_secret_type(
        self, secret_type: SecretType
    ) -> list[tuple[str | int | bytes]]:
        """
        Retrieves all entries for a specific secret type.

        :param secret_type: ``SecretType`` -> The type of secret to filter by
        :return: ``list[tuple[str | int]]`` -> A list of tuples containing entries for the specified secret type
        """
        secrets = self.__available_secrets()
        by_secret_type = []
        for entry in secrets:
            id_, name, secret, *_ = entry
            if secret == secret_type.value:
                by_secret_type.append(entry)
        return by_secret_type

    def get_keys_by_secret_type(
        self, secret_type: SecretType
    ) -> list[tuple[str | int]]:
        """
        Retrieves all keys (name, secret) for a specific secret type.

        :param secret_type: ``SecretType`` -> The type of secret to filter by
        :return: ``list[tuple[str | int]]`` -> A list of tuples containing keys for the specified secret type
        """
        secrets = self.__available_secrets()
        by_secret_type = []
        for entry in secrets:
            id_, name, secret, *_ = entry
            if secret == secret_type.value:
                by_secret_type.append(self.retrieve_secret(f"id = {id_}"))
        return by_secret_type

    def generic_get_secrets(self, secret_type, model_cls, field_map):
        """
        Retrieve secrets of a given type and map them to a dataclass.

        :param secret_type: ``SecretType`` -> The type of secret to retrieve
        :param model_cls: ``type`` -> The dataclass type to map the retrieved secrets to
        :param field_map: ``dict`` -> A mapping of field names to dataclass field values
        :return: ``list[model_cls]`` | ``None`` -> A list of instances of the dataclass or None if no secrets found
        """
        entries = self.get_entries_by_secret_type(secret_type)
        instances = [
            model_cls(**{k: inst[v] for k, v in field_map.items()})
            for inst in entries
            if isinstance(inst, tuple)
        ]
        return instances if instances else None

    def generic_store_secret(
        self, name: str, secret_type: SecretType, secret: str, metadata: str = ""
    ):
        """
        Store a secret in the database.
        This method adds a new secret entry to the database with the specified name, type, secret value, and metadata.

        :param name: ``str`` -> The name of the secret entry
        :param secret_type: ``SecretType`` -> The type of the secret entry
        :param secret: ``str`` -> The secret value to be stored
        :param metadata: ``str`` -> Additional metadata associated with the secret entry
        :return: ``bool`` -> True if the secret was added successfully, False otherwise
        """
        return self.__add_secret(name, secret_type, secret, metadata)

    def generic_update_secret(
        self, name: str, secret_type: SecretType, new_secret: str
    ):
        """
        Update a secret.
        This method updates the secret value of an existing secret entry identified by its name.

        :param name: ``str`` -> The name of the secret entry to update
        :param new_secret: ``str`` -> The new secret value to be stored
        :param secret_type: ``SecretType`` -> The type of the secret entry
        :return: ``bool`` -> True if the secret was updated successfully, False otherwise
        """
        # For validation purposes only
        entry = self.retrieve_entry_by_name(name)
        if not entry:
            logging.error(f"Secret for {name} not found.")
            return False
        return self.__update_secret(name, secret_type, new_secret)
