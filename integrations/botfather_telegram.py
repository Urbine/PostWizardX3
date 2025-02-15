"""
Telegram BotFather integration for ``webmaster-seo-tools``
In the present application, only ``getMe`` and ``SendMessage`` are needed.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import os
import requests
from requests import Response  # Imported for typing purposes.

# Local imports
from core import bot_father
from core.config_mgr import BotAuth  # Imported for typing purposes.
from integrations.url_builder import BotFatherCommands, BotFatherEndpoints


def get_me(b_father: BotAuth, b_commands: BotFatherCommands) -> Response:
    """Get basic information about the bot and will tell users whether
    a bot has been configured and other options such as the ability to join groups, etc.

    :param b_father: ``BotAuth`` Authentication dataclass found in ``core.config_mgr``
    :param b_commands: ``BotFatherCommands`` Commands dataclass for the Telegram BotFather integration.
    :return: ``Response`` (Extract ``.json`` object if applicable)
    """
    headers = {
        # application/json (except for uploading files)
        "Content-Type": "application/json",
    }
    url = b_commands.api_url
    token = b_father.token
    return requests.get(f"{url}{token}{b_commands.get_me}", headers=headers)


def send_message(
    b_father: BotAuth,
    b_commands: BotFatherCommands,
    b_endpoints: BotFatherEndpoints,
    msg_txt: str,
) -> Response:
    """Send message to the channel or group configured in ``workflows_config.ini``
    In order that you can use this function, the telegram bot has to be added to that chat or group.

    :param b_father: ``BotAuth`` Authentication dataclass found in ``core.config_mgr``
    :param b_commands: ``BotFatherCommands`` Commands dataclass for the Telegram BotFather integration.
    :param b_endpoints: ``BotFatherEndpoints`` Builder dataclass holding Telegram API endpoints.
    :param msg_txt: ``str`` - Message text to be sent to the group or channel
    :return: ``Response``
    """
    url = b_commands.api_url
    token = b_father.token
    chat_id = f"{b_endpoints.chat_id}{b_father.telegram_chat_id}"
    text = f"{b_endpoints.text}{msg_txt}"
    os.environ["T_CHAT_ID"] = b_father.telegram_chat_id
    req = requests.get(
        f"{url}{token}{b_commands.send_message}{chat_id}{text}"
        + '&disable_notification=true&link_preview_options={"is_disabled":false,"prefer_large_media":true}'
    )
    return req


if __name__ == "__main__":
    args = argparse.ArgumentParser(
        description="Telegram BotFather CLI for webmaster-seo-tools."
    )

    args.add_argument(
        "--msg",
        type=str,
        help="Send a text message to the group or channel in your configuration file.",
    )

    args.add_argument(
        "--getme",
        action="store_true",
        help="Get information about your bot and configuration options for BotFather.",
    )

    args_cli = args.parse_args()

    if args_cli.msg is not None:
        print(
            send_message(
                bot_father(), BotFatherCommands(), BotFatherEndpoints(), args_cli.msg
            ).json()
        )
    elif args_cli.getme:
        print(get_me(bot_father(), BotFatherCommands()).json())
    else:
        quit(0)
