"""
PostWizard API Utilities - Common Operations
This module contains utility functions for interacting with the PostWizard API.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Dict, List, Union, Optional

# Third-party imports
import requests

# Local imports
from postwizard_sdk.builders.api_url_builder import APIUrlBuilder
from postwizard_sdk.builders import PostMetaPayload, PostInfoPayload
from postwizard_sdk.builders.interfaces import PayloadBuilder
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


def get_all_post_meta() -> List[Dict[str, Union[str, int, bool, None]]]:
    """
    Retrieves all post metadata from the PostWizard API.
    This function sends a GET request to the PostWizard API to retrieve all post metadata.

    :return: ``List[Dict[str, Union[Optional[str, int, bool]]]]`` -> List of dictionaries containing post metadata.
    """
    api_addr = APIUrlBuilder().post_meta_dump()
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.get(api_addr.build(), headers=token_headers)
    return request_info.json()


def send_batch_payload(
    api_addr: APIUrlBuilder, payloads: List[PayloadBuilder]
) -> Dict[str, Union[str, int, List[int]]]:
    """
    Sends a batch of payloads to the PostWizard API.
    This function sends a POST request to the PostWizard API to update the metadata of multiple posts.

    :param api_addr: ``APIUrlBuilder`` -> The API URL builder object.
    :param payloads: ``List[PayloadBuilder]`` -> The list of payloads to send.
    :return: ``Dict[str, Union[str, int, List[int]]]`` -> The response from the PostWizard API.
    """
    token_headers = PostWizardAuth.bearer_auth_flow()
    payload = [dict(builder.build()) for builder in payloads]
    request_info = requests.post(api_addr.build(), headers=token_headers, json=payload)
    return request_info.json()


def send_meta_batch_job(
    payload: List[PostMetaPayload],
) -> Dict[str, Union[str, int, List[int]]]:
    """
    Specialised method that sends a batch of metadata updates to the PostWizard API.

    :param payload: ``List[PostMetaPayload]`` -> The list of payloads containing the metadata to update.
    :return: ``Dict[str, Union[str, int, List[int]]]`` -> The response from the PostWizard API.
    """
    api_addr = APIUrlBuilder().post_meta_batch()
    return send_batch_payload(api_addr, payload)


def send_post_batch_job(
    payload: List[PostInfoPayload],
) -> Dict[str, Union[str, int, List[int]]]:
    """
    Specialised method that sends a batch of post updates to the PostWizard API.

    :param payload: ``List[PostInfoPayload]`` -> The list of payloads containing the post information to update.
    :return: ``Dict[str, Union[str, int, List[int]]]`` -> The response from the PostWizard API.
    """
    api_addr = APIUrlBuilder().post_batch()
    return send_batch_payload(api_addr, payload)
