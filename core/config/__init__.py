"""
Core configuration module for the project.

This module provides the functionality to create and manage configuration files for the PostWizard project.
It includes functions to read configuration templates and create initial configuration files.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


import os
from typing import Optional

# Locally implemented modules
from core.models.file_system import ApplicationPath, ProjectFile
from core.utils.file_system import remove_if_exists, write_to_file, goto_project_root

# Path to the directory containing config templates
goto_project_root("PostWizardX3", __file__)


def read_template(template_path):
    """Read the contents of a config template file."""
    with open(template_path, "r") as f:
        return f.read()


def create_workflows_config(repair_from_template: bool = False) -> Optional[bool]:
    """Create the workflows configuration file using a template."""
    config_path = ApplicationPath.CONFIG.value
    new_filename = ProjectFile.WORKFLOWS_CONFIG.value
    if repair_from_template:
        return remove_if_exists(os.path.join(config_path, new_filename))

    workflows_config_content = read_template(
        ProjectFile.WORKFLOWS_CONFIG_TEMPLATE.value
    )
    write_to_file(
        new_filename,
        config_path,
        "ini",
        workflows_config_content,
        create_file=True,
    )
    return None
