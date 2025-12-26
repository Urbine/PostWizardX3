# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
PostWizardX3 configuration setup.

Creates initial project structure and configuration files.
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os

# Locally implemented modules
from core.utils.file_system import goto_project_root
from core.config import create_workflows_config
from core.models.file_system import ApplicationPath


if __name__ == "__main__":
    print("Welcome to the configuration create module.")
    print("This module will generate configuration templates for the utilities.")
    print(
        "Review the changes and modify the fields as needed once the files are generated.\n"
    )
    goto_project_root("PostWizardX3", __file__)

    # Setup up your logging directory before running this script
    logs_directory = os.path.join(
        ApplicationPath.CORE_PKG.value, ApplicationPath.LOGGING.value
    )
    config_directory = os.path.join(
        ApplicationPath.CORE_PKG.value, ApplicationPath.CONFIG.value
    )

    os.makedirs(logs_directory, exist_ok=True)
    os.makedirs(config_directory, exist_ok=True)

    # You can customize the template in the ``templates`` directory.
    create_workflows_config()
