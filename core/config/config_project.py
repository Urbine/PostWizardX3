"""
PostDirector configuration setup.

Creates initial project structure and configuration files.
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os

# Locally implemented modules
from core.utils.helpers import goto_project_root
from core.config import create_workflows_config


if __name__ == "__main__":
    print("Welcome to the configuration create module.")
    print("This module will generate configuration templates for the utilities.")
    print(
        "Review the changes and modify the fields as needed once the files are generated.\n"
    )
    goto_project_root("PostDirector", __file__)

    # Setup up your logging directory before running this script
    logs_directory = os.path.join(os.getcwd(), "logs")
    config_directory = os.path.join(os.getcwd(), "core", "config")

    os.makedirs(logs_directory, exist_ok=True)
    os.makedirs(config_directory, exist_ok=True)

    # You can customize the template in the ``templates`` directory.
    create_workflows_config()
