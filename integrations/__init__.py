"""
Integrations used throughout the project modules and workflows.
This package groups modules interacting with external services or APIs.

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = '1.0.0'

# Adult Next API is not included here yet since it works as a standalone
# program, and it is not meant to work as a module yet.

# Callback Server `callback_server.py`
from integrations.callback_server import run_callback_server

# WordPress API (Local implementation `wordpress_api`)
from integrations.wordpress_api import create_tag_report_excel
from integrations.wordpress_api import create_wp_local_cache
from integrations.wordpress_api import curl_wp_self_concat
from integrations.wordpress_api import get_from_class_list
from integrations.wordpress_api import get_post_category
from integrations.wordpress_api import get_post_descriptions
from integrations.wordpress_api import get_post_models
from integrations.wordpress_api import get_post_titles_local
from integrations.wordpress_api import get_slugs
from integrations.wordpress_api import get_tag_count
from integrations.wordpress_api import get_tag_id_pairs
from integrations.wordpress_api import get_tags_num_count
from integrations.wordpress_api import get_tags_unique
from integrations.wordpress_api import local_cache_config
from integrations.wordpress_api import map_posts_by_id
from integrations.wordpress_api import map_postsid_category
from integrations.wordpress_api import map_tags_post_urls
from integrations.wordpress_api import map_tags_posts
from integrations.wordpress_api import map_wp_class_id
from integrations.wordpress_api import tag_id_count_merger
from integrations.wordpress_api import tag_id_merger_dict
from integrations.wordpress_api import unpack_tpl_excel
from integrations.wordpress_api import update_json_cache
from integrations.wordpress_api import update_published_titles_db
from integrations.wordpress_api import upgrade_wp_local_cache
from integrations.wordpress_api import upload_thumbnail
from integrations.wordpress_api import wp_post_create

__all__ = ['create_tag_report_excel',
           'create_wp_local_cache',
           'curl_wp_self_concat',
           'get_from_class_list',
           'get_post_category',
           'get_post_descriptions',
           'get_post_models',
           'get_post_titles_local',
           'get_slugs',
           'get_tag_count',
           'get_tag_id_pairs',
           'get_tags_num_count',
           'get_tags_unique',
           'map_postsid_category',
           'map_posts_by_id',
           'map_tags_posts',
           'map_tags_post_urls',
           'map_wp_class_id',
           'local_cache_config',
           'run_callback_server',
           'tag_id_merger_dict',
           'tag_id_count_merger',
           'unpack_tpl_excel',
           'update_json_cache',
           'update_published_titles_db',
           'upload_thumbnail',
           'upgrade_wp_local_cache',
           'wp_post_create']
