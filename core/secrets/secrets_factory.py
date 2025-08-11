import os
import platform
import socket
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet

import core
import core.utils.file_system
import core.utils.strings
from .secret_repository import SecretsDBInterface
from . import (
    KEY_DIR,
    KEY_NAME,
    VAULT_DIR,
    SECRETS_DIR,
    LOCAL_VAULT_NAME,
    LOCAL_TEST_VAULT_NAME,
)


def initialize_key_file() -> Path:
    """
    Initializes the key file for the vault directory.
    If the key file already exists, it will return the path to the existing key file.
    If the key file does not exist, it will create a new key file with a generated key.
    The key file is stored in the "keys" directory within the ``core`` directory.

    :return: ``Path`` -> The path to the key file.
    """
    keys_dir = KEY_DIR
    os.makedirs(os.path.join(SECRETS_DIR, keys_dir), exist_ok=True)
    # Only one key in the vault directory is allowed
    keys_in_dir = core.utils.file_system.search_files_by_ext(
        "key", keys_dir, abspaths=True
    )
    if keys_in_dir:
        return Path(keys_in_dir[0])
    else:
        key = Fernet.generate_key()
        with open(key_path := os.path.join(keys_dir, KEY_NAME), "wb") as key_file:
            key_file.write(key)
        core.utils.file_system.apply_os_permissions(
            key_path := Path(key_path), read_only=True
        )
        return key_path


def initialize_vault(test_mode: bool = False) -> None:
    """
    Initializes the vault directory and creates the secrets database if it does not exist.
    If the vault directory does not exist, it will be created.
    If the database file does not exist, it will be created with the necessary table structure.

    :param test_mode: ``bool`` -> If True, the function will create a temporary vault directory
    :return: ``None`` -> This function does not return anything.
    """
    vault_db_name = LOCAL_VAULT_NAME if not test_mode else LOCAL_TEST_VAULT_NAME
    vault_path = os.path.join(
        VAULT_DIR, core.utils.strings.clean_filename(vault_db_name, "db")
    )
    if not (dir_exists := os.path.exists(VAULT_DIR)) or not os.path.exists(vault_path):
        if not dir_exists:
            os.makedirs(VAULT_DIR, exist_ok=True)
            core.utils.file_system.apply_os_permissions(VAULT_DIR, dir_permissions=True)
        try:
            connection, cursor = core.utils.file_system.create_store(vault_path)
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
            raise OpErr
    else:
        connection, cursor = core.utils.file_system.create_store(vault_path)
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
    initialize_key_file()
    initialize_vault(test_mode=test_mode)
    return SecretsDBInterface(
        Path(
            VAULT_DIR,
            core.utils.strings.clean_filename(
                LOCAL_VAULT_NAME if not test_mode else LOCAL_TEST_VAULT_NAME, "db"
            ),
        ),
        in_memory=in_memory,
    )
