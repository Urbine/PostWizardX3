"""
File system models for the project.

This module defines the ApplicationPath and ProjectFile enums,
which represent the paths and filenames used in the project.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
import platform
import socket
from datetime import datetime
from enum import Enum
from pathlib import Path


class ApplicationPath(Enum):
    """Enum for application paths and directories in the project."""

    PROJECT_ROOT = "PostWizardX3"
    ARTIFACTS = Path("artifacts")
    CONFIG = Path("config")
    CACHE = Path("cache")
    SECRETS = Path("secrets")
    TEMPORARY = os.path.join("cache", "tmp")
    TEMPLATES = os.path.join("core", "config", "templates")
    REPORTS = os.path.join("artifacts", "reports")
    WP_POSTS_CACHE = os.path.join("cache", "wordpress", "wp-posts.json")
    WP_PHOTOS_CACHE = os.path.join("cache", "wordpress", "wp-photos.json")
    KEY_DIR = os.path.join("core", "secrets", "keys")
    VAULT_DIR = os.path.join("core", "secrets", "vault")
    ML_ENGINE_PKG = "ml_engine.ml_models"
    CONFIG_PKG = "core.config"
    CORE_PKG = "core"
    LOGGING = "logs"


class ProjectFile(Enum):
    """Enum for vital filenames in the project."""

    EXCEL_REPORT = f"tag-report-excel-{datetime.today()}.xlsx"
    WORKFLOWS_CONFIG = "workflows_config.ini"
    WORKFLOWS_CONFIG_TEMPLATE = "workflows_config_template.ini"
    KEY_NAME = "vault_access.key"
    LOCAL_TEST_VAULT_NAME = "test_vault"
    LOCAL_VAULT_NAME = (
        f"{os.getlogin()}_{socket.getfqdn()}_{platform.system()}_{platform.machine()}"
    )
