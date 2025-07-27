import os
from pathlib import Path
import platform
import socket

BASE_DIR = Path(__file__).parent
KEY_DIR = os.path.join(BASE_DIR, "keys")
VAULT_DIR = os.path.join(BASE_DIR, "vault")
KEY_NAME = "vault_access.key"
SECRETS_DIR = os.path.split(__file__)[0]
LOCAL_VAULT_NAME = (
    f"{os.getlogin()}_{socket.getfqdn()}_{platform.system()}_{platform.machine()}"
)
LOCAL_TEST_VAULT_NAME = "test_vault"

__all__ = [
    "BASE_DIR",
    "KEY_DIR",
    "VAULT_DIR",
    "KEY_NAME",
    "SECRETS_DIR",
    "LOCAL_VAULT_NAME",
    "LOCAL_TEST_VAULT_NAME",
]
