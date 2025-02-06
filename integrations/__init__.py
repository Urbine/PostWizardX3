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
from integrations.url_builder import WPEndpoints, XEndpoints

# Callback Server `callback_server.py`
from integrations.callback_server import run_callback_server

# WordPress API (Local implementation `wordpress_api`)
from integrations.wordpress_api import (
    curl_wp_self_concat,
    get_post_category,
    get_post_descriptions,
    get_post_titles_local,
    get_slugs,
    get_links,
    map_wp_class_id,
    tag_id_merger_dict,
    update_json_cache,
    upload_thumbnail,
    wp_post_create,
)


__all__ = [
    "curl_wp_self_concat",
    "get_post_category",
    "get_post_descriptions",
    "get_post_titles_local",
    "get_slugs",
    "get_links",
    "map_wp_class_id",
    "run_callback_server",
    "tag_id_merger_dict",
    "update_json_cache",
    "upload_thumbnail",
    "wp_post_create",
    "WPEndpoints",
    "XEndpoints",
]
