"""
PostWizard API Validation Utilities

This module contains utility functions for validating data for and from the PostWizard API
making them useful for validating payload data before sending it to the PostWizard service.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import asyncio
from collections import deque
from typing import Dict, List, Union
from types import MappingProxyType

# Third-party imports
import aiohttp

# Local imports
from postwizard_sdk.models import PostMetaKey
from postwizard_sdk.builders import PostMetaPayload


def bulk_test_video_url(
    post_list: List[PostMetaPayload] | List[Dict[str, Union[str, int, bool, None]]],
) -> List[MappingProxyType[str, Union[str, int, bool, None]]]:
    """
    Bulk tests video URLs for validity.
    This function uses asyncio to test multiple video URLs concurrently,
    limiting the number of concurrent connections to 5. Returns a list of immutable posts with failed video URLs.

    :param post_list: ``List[PostMetaPayload] | List[Dict[str, Union[str, int, bool, None]]]'' List of posts to test.
    :return: ``List[MappingProxyType[str, Union[str, int, bool, None]]]`` -> List of posts with failed video URLs.
    """
    failed_links = deque()
    semaphore = asyncio.Semaphore(5)
    failed_urls_lock = asyncio.Lock()

    async def mutate_failed_urls_deque(elem):
        async with failed_urls_lock:
            failed_links.append(MappingProxyType(elem))

    async def test_link(session, post):
        video_url = post[PostMetaKey.VIDEOURL.value]
        if not video_url:
            return
        else:
            async with semaphore:
                async with session.get(video_url) as response:
                    if response.status != 200:
                        await mutate_failed_urls_deque(post)

    async def run_all():
        async with aiohttp.ClientSession(
            headers={"keep-alive": "True"},
            timeout=aiohttp.ClientTimeout(30),
            connector=aiohttp.TCPConnector(ssl_shutdown_timeout=10.0, force_close=True),
        ) as main_session:
            tasks = [
                test_link(
                    main_session,
                    post.build() if isinstance(post, PostMetaPayload) else post,
                )
                for post in post_list
            ]
            await asyncio.gather(*tasks)

    asyncio.run(run_all())

    return list(failed_links)
