"""
PostWizard API Utilities - Common Operations
This module contains utility functions for interacting with the PostWizard API.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

# Third-party imports
import requests

# Local imports
from postwizard_sdk.builders.api_url_builder import APIUrlBuilder
from postwizard_sdk.builders import PostMetaPayload, PostInfoPayload
from postwizard_sdk.utils.auth import PostWizardAuth


def update_post_meta(payload: PostMetaPayload, post_id: int) -> int:
    """
    Updates the meta fields of a post.
    This function sends a POST request to the PostWizard API to update the metadata of a post.

    :param payload: ``PostMetaPayload`` -> The payload containing the metadata to update.
    :param post_id: ``int`` -> The ID of the post to update.
    :return: ``int`` -> The HTTP status code of the response.
    """
    api_addr = APIUrlBuilder().posts_meta(post_id)
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.post(
        api_addr.build(), headers=token_headers, json=dict(payload.build())
    )
    return request_info.status_code


def update_post_bypass(payload: PostInfoPayload, post_id: int) -> int:
    """
    Updates the fields of a post.
    This function sends a POST request to the PostWizard API to update the details of a post.
    This function bypasses the WordPress API and uses the PostWizard API directly on the server database.

    :param payload: ``PostInfoPayload`` -> The payload containing the metadata to update.
    :param post_id: ``int`` -> The ID of the post to update.
    :return: ``int`` -> The HTTP status code of the response.
    """
    api_addr = APIUrlBuilder().posts(post_id)
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.post(
        api_addr.build(), headers=token_headers, json=payload.build()
    )
    return request_info.status_code
