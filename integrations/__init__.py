"""
Integrations used throughout the project modules and workflows.
This package groups modules interacting with external services or APIs.

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = "1.0.0"

# Adult Next API is not included here yet since it works as a standalone
# program, and it is not meant to work as a module yet.

# WordPress Endpoints for use in external integrations with it.
from integrations.x_api import XEndpoints
from integrations.wordpress_api import WPEndpoints

# Callback Server `callback_server.py`
from integrations.callback_server import run_callback_server, callback_server_sub


__all__ = ["XEndpoints", "WPEndpoints", "run_callback_server", "callback_server_sub"]
