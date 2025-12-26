# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Secrets factory module

This module provides configuration functions and a factory for creating a SecretsDBInterface instance
to be used as a central repository of secrets.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet

# Local imports
from core.utils.file_system import (
    apply_os_permissions,
    create_store,
    search_files_by_ext,
)
from core.utils.file_system import clean_filename, goto_project_root
from .secret_repository import SecretsDBInterface
from ..models.file_system import ApplicationPath, ProjectFile


def initialize_key_file() -> Path | str:
    """
    Initializes the key file for the vault directory.
    If the key file already exists, it will return the path to the existing key file.
    If the key file does not exist, it will create a new key file with a generated key.
    The key file is stored in the "keys" directory within the ``core`` directory.

    :return: ``Path`` -> The path to the key file.
    """
    keys_dir = ApplicationPath.KEY_DIR.value
    os.makedirs(keys_dir, exist_ok=True)
    # Only one key in the vault directory is allowed
    keys_in_dir = search_files_by_ext("key", keys_dir, abspaths=True)
    if keys_in_dir:
        return Path(keys_in_dir[0])
    else:
        key = Fernet.generate_key()
        key_path = os.path.join(keys_dir, ProjectFile.KEY_NAME.value)
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        apply_os_permissions(key_path, read_only=True)
        return key_path


def initialize_vault(test_mode: bool = False) -> None:
    """
    Initializes the vault directory and creates the secrets database if it does not exist.
    If the vault directory does not exist, it will be created.
    If the database file does not exist, it will be created with the necessary table structure.

    :param test_mode: ``bool`` -> If True, the function will create a temporary vault directory
    :return: ``None`` -> This function does not return anything.
    """
    vault_db_name = (
        ProjectFile.LOCAL_VAULT_NAME.value
        if not test_mode
        else ProjectFile.LOCAL_TEST_VAULT_NAME.value
    )
    vault_directory = ApplicationPath.VAULT_DIR.value
    vault_path = os.path.join(vault_directory, clean_filename(vault_db_name, "db"))
    if not (dir_exists := os.path.exists(vault_directory)) or not os.path.exists(
        vault_path
    ):
        if not dir_exists:
            os.makedirs(vault_directory, exist_ok=True)
            apply_os_permissions(vault_directory, dir_permissions=True)
        try:
            connection, cursor = create_store(vault_path)
            secret_mgr_table = """
            CREATE TABLE secrets(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                secret_type TEXT NOT NULL,
                secret BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(secret_mgr_table)
            connection.commit()
        except sqlite3.OperationalError as OpErr:
            logging.exception("Raised OperationalError while initializing vault", OpErr)
            raise OpErr
    else:
        connection, cursor = create_store(vault_path)
        cursor.close()
        connection.close()
    return None


def secrets_factory(
    test_mode: bool = False, in_memory: bool = False
) -> SecretsDBInterface:
    """
    Factory function for the SecretsDBInterface class.
    This function initializes the key file and the database connection,
    and returns an instance of the SecretsDBInterface class.

    :param in_memory: ``bool`` -> If True, the function will create an in-memory database
    :param test_mode: ``bool`` -> If True, the function will create a temporary vault directory
    :return: ``SecretsDBInterface`` -> An instance of the SecretsDBInterface class.
    """
    goto_project_root(ApplicationPath.PROJECT_ROOT.value, __file__)
    initialize_key_file()
    initialize_vault(test_mode=test_mode)
    return SecretsDBInterface(
        Path(
            ApplicationPath.VAULT_DIR.value,
            clean_filename(
                ProjectFile.LOCAL_VAULT_NAME.value
                if not test_mode
                else ProjectFile.LOCAL_TEST_VAULT_NAME.value,
                "db",
            ),
        ),
        in_memory=in_memory,
    )
