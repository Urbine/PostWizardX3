# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Workflows Social Module

This module is responsible for mediating between local social media integrations and workflows
by providing additional functionality and adapting them to the
requirements of the flows.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import random
from typing import Optional, Union

# Third-party imports
import pyclip
from rich.console import Console

# Local imports
from core.config.config_factories import general_config_factory, social_config_factory
from core.models.config_model import (
    MCashContentBotConf,
    MCashGalleryBotConf,
    EmbedAssistBotConf,
)
from core.models.secret_model import SecretType
from core.utils.secret_handler import SecretHandler
from integrations import x_api, XEndpoints, botfather_telegram
from integrations.botfather_telegram import BotFatherCommands, BotFatherEndpoints
from wordpress import WordPress
from workflows.utils.logging import ConsoleStyle


def x_post_creator(
    description: str, post_url: str, post_text: Optional[str] = None
) -> int:
    """Create a post with a random action call for the X platform.
    Depending on your bot configuration, you can pass in your own post text and
    override the random call to action. If you just don't feel like typing and
    want to post without the randon text, the default value is an empty string.

    Set the ``x_posting_auto`` option in ``workflows_config.ini`` to ``False`` ,
    so that you get to type when you interact with the flows.

    :param description: ``str`` Video description
    :param post_url: ``str`` Video post url on WordPress
    :param post_text: ``str`` in certain circumstances
    :return: ``int`` POST request status code.
    """
    cs_conf = general_config_factory()
    site_name = cs_conf.site_name
    calls_to_action = [
        f"Watch more on {site_name}:",
        f"Take a quick look on {site_name}:",
        f"Watch the action for free on {site_name}:",
        f"Don't miss out. Watch now on {site_name}:",
        f"Don't miss out. Watch more on {site_name}:",
        f"Watch for free on {site_name}:",
        "Click below to watch for free:",
        "You won't need another video after this one:",
        f"{site_name} has it all for free:",
        f"All the Good stuff. Only on {site_name}:"
        "I bet you haven't watched this one:"
        "Well, you asked for it:",
        "I can't believe this is free:",
        "Specially for you:",
        f"Check out {site_name} today:",
        "Watch today for free:",
        "You're missing out on the action:",
        "When you thought you've watch it all:",
        f"Brought to you by {site_name}:",
        "Watch now:",
        "Watch free:Click to watch full video:",
        "Don't miss out:",
    ]
    # Env variable "X_TOKEN" is assigned in function ``x_api.refresh_flow()``
    bearer_token = os.environ.get("X_TOKEN")

    if post_text or post_text == "":
        post_text = f"{description} {post_text} {post_url}"
    else:
        post_text = f"{description} | {random.choice(calls_to_action)} {post_url}"

    request = x_api.post_x(post_text, bearer_token, XEndpoints())
    logging.info(f"Sent to X -> {post_text}")
    logging.info(f"X post metadata -> {request.json()}")
    return request.status_code


def telegram_send_message(
    description: str,
    post_url: str,
    msg_text: str = "",
) -> int:
    """Set up a message template for the Telegram BotFather function ``send_message()``
    Parameters are self-explanatory.

    :param description: ``str``
    :param msg_text: ``str``
    :param post_url: ``str``
    :return: ``int``
    """
    general_config = general_config_factory()
    social_config = social_config_factory()
    site_name = general_config.site_name
    calls_to_action = [
        f"Watch more on {site_name}:",
        f"Take a quick look on {site_name}:",
        f"Watch the action for free on {site_name}:",
        f"Don't miss out. Watch now on {site_name}:",
        f"Don't miss out. Watch more on {site_name}:",
        f"Watch for free on {site_name}:",
        "Click below to watch for free:",
        "You won't need another video after this one:",
        f"{site_name} has it all for free:",
        f"All the Good stuff. Only on {site_name}:"
        "I bet you haven't watched this one:"
        "Well, you asked for it:",
        "I can't believe this is free:",
        "Specially for you:",
        f"Check out {site_name} today:",
        "Watch today for free:",
        "You're missing out on the action:",
        "When you thought you've watch it all:",
        f"Brought to you by {site_name}:",
        "Watch now:",
        "Watch free:Click to watch full video:",
        "Don't miss out:",
    ]
    auto_mode = social_config.telegram_sharing_auto
    if auto_mode:
        msg_text = random.choice(calls_to_action)

    message = (
        f"{description} | {msg_text} {post_url}"
        if auto_mode
        else f"{description} {msg_text} {post_url}"
    )
    req = botfather_telegram.send_message(
        SecretHandler().get_secret(SecretType.TELEGRAM_ACCESS_TOKEN)[0],
        BotFatherCommands(),
        BotFatherEndpoints(),
        message,
    )
    logging.info(f"Sent to Telegram -> {message}")
    logging.info(f"BotFather post metadata -> {req.json()}")
    return req.status_code


def social_sharing_controller(
    console_obj: Console,
    description: str,
    wp_slug: str,
    cs_config: Union[MCashContentBotConf, MCashGalleryBotConf, EmbedAssistBotConf],
    wordpress_site: WordPress,
) -> None:
    """Share WordPress posts to social media platforms based on the settings in the workflow config.
    It is able to identify whether X or Telegram workflows have been enabled and post content accordingly.

    :param console_obj: ``rich.console.Console`` Console object used to provide user feedback
    :param description: ``str`` description/caption that will be shared
    :param wp_slug: ``str`` WordPress slug used to identify the published post
    :param cs_config: ``MCashContentBotConf`` | ``MCashGalleryBotConf`` | ``EmbedAssistBotConf``
    :param wordpress_site: ``WordPress`` class instance responsible for managing all the
                             WordPress site data
    :return: ``None``
    """
    if cs_config.x_posting_enabled or cs_config.telegram_sharing_enabled:
        status_msg = "Checking WP status and preparing for social sharing."
        status_style = ConsoleStyle.TEXT_STYLE_ACTION.value
        user_input = ConsoleStyle.TEXT_STYLE_ATTENTION.value
        with console_obj.status(
            f"[{status_style}]{status_msg} [blink]ε= ᕕ(⎚‿⎚)ᕗ[blink] [/{status_style}]\n",
            spinner="earth",
        ):
            is_published = wordpress_site.post_polling(wp_slug)
        if is_published:
            logging.info(
                f"Post {wp_slug} has been published. Exceptions after this might be caused by social plugins."
            )
            if cs_config.x_posting_enabled:
                logging.info("X Posting - Enabled in workflows config")
                if cs_config.x_posting_auto:
                    logging.info("X Posting Automatic detected in config")
                    # Environment "LATEST_POST" variable assigned in by the ``post_polling()`` function
                    # in the ``WordPress`` class.
                    x_post_create = x_post_creator(
                        description, os.environ.get("LATEST_POST")
                    )
                else:
                    post_text = console_obj.input(
                        f"[{user_input}]Enter your additional X post text here or press enter to use default configs: [{user_input}]\n"
                    )
                    logging.info(f"User entered custom post text: {post_text}")
                    x_post_create = x_post_creator(
                        description,
                        os.environ.get("LATEST_POST"),
                        post_text=post_text,
                    )

                    # Copy custom post text for the following prompt
                    pyclip.detect_clipboard()
                    pyclip.copy(post_text)

                if x_post_create == 201:
                    console_obj.print(
                        "--> Post has been published on WP and shared on X.\n",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                else:
                    console_obj.print(
                        f"--> There was an error while trying to share on X.\n Status: {x_post_create}",
                        style=ConsoleStyle.TEXT_STYLE_WARN.value,
                    )
                logging.info(f"X post status code: {x_post_create}")

            if cs_config.telegram_sharing_enabled:
                logging.info("Telegram Posting - Enabled in workflows config")
                if cs_config.telegram_sharing_auto:
                    logging.info("Telegram Posting Automatic detected in config")
                    telegram_msg = telegram_send_message(
                        description,
                        os.environ.get("LATEST_POST"),
                    )
                else:
                    post_text = console_obj.input(
                        f"[{user_input}]Enter your additional Telegram message here or press enter to use default configs: [{user_input}]\n"
                    )
                    telegram_msg = telegram_send_message(
                        description,
                        os.environ.get("LATEST_POST"),
                        msg_text=post_text,
                    )

                if telegram_msg == 200:
                    console_obj.print(
                        # Env variable assigned in botfather_telegram.send_message()
                        f"--> Message sent to Telegram {os.environ.get('T_CHAT_ID')}",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                else:
                    console_obj.print(
                        f"--> There was an error while trying to communicate with Telegram.\n Status: {telegram_msg}",
                        style=ConsoleStyle.TEXT_STYLE_WARN.value,
                    )
                logging.info(f"Telegram message status code: {telegram_msg}")
