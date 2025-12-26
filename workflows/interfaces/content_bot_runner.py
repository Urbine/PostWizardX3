# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
BotRunner base class
This module contains the base class for all bot flows and
provides an interface to manage initialization logic.

``BotRunner`` uses, whenever possible, lazy imports to
reduce the amount of code loaded at runtime and improve initialization time.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os

from abc import ABC, abstractmethod
from typing import List, Tuple, Generic, TypeVar

from core.config.config_factories import general_config_factory, social_config_factory
from core.models import WorkflowConfigObject
from core.utils.file_system import ApplicationPath
from core.utils.secret_handler import SecretHandler
from core.models.secret_model import SecretType, WPSecrets
from workflows.utils.logging import ConsoleStyle

W_co = TypeVar("W_co", covariant=True, bound=WorkflowConfigObject)


class ContentBotRunner(ABC, Generic[W_co]):
    """
    BotRunner base class

    This class provides an interface to manage initialization logic.

    :param workflow_config: Workflow configuration object.
    :param parent: ``True`` if the bot is running in a parent directory. Default ``False``.
    """

    def __init__(
        self, workflow_config: W_co, interactive: bool = True, parent: bool = False
    ):
        self._bot_config = workflow_config
        self._parent = parent
        self._interactive = interactive
        self._general_config = general_config_factory()
        self._social_config = social_config_factory()
        self._query = None
        self._action_style = ConsoleStyle.TEXT_STYLE_ACTION.value
        self._attention_style = ConsoleStyle.TEXT_STYLE_ATTENTION.value
        self._warning_style = ConsoleStyle.TEXT_STYLE_WARN.value
        self._prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
        self._default_style = ConsoleStyle.TEXT_STYLE_DEFAULT.value

        # Deferred assignment
        self._console = None
        self._site = None
        self._partner = None
        self._partner_db_name = None
        self._cursor = None
        self._query_result = None
        self._ready_posts = None
        self._total_ready = None
        self._thumbnails_dir = None

    def _logging_setup(self):
        from core.utils.file_system import logging_setup
        from core.models.file_system import ApplicationPath

        if self._general_config.enable_logging:
            logging_setup(ApplicationPath.LOGGING.value, __file__)
            logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}")

    def _console_setup(self) -> None:
        from rich.console import Console
        from core.utils.system_shell import clean_console

        if os.name == "posix":
            import readline  # noqa: F401
        clean_console()
        self._console = Console()
        return None

    def _refresh_token_setup(self):
        if self._social_config.x_posting:
            from integrations import x_api
            from workflows.utils.initialise import XEndpoints

            if social_config_factory().x_posting:
                x_api.refresh_flow(
                    SecretHandler().get_secret(SecretType.X_REFRESH_TOKEN)[0],
                    XEndpoints(),
                )

    def _wp_setup(self):
        from wordpress import WordPress
        from core.models.config_model import MCashContentBotConf, EmbedAssistBotConf

        wp_auth: WPSecrets = SecretHandler().get_secret(SecretType.WP_APP_PASSWORD)[0]
        logging.info(f"Loaded WP Auth: {wp_auth}")
        if isinstance(self._bot_config, (MCashContentBotConf, EmbedAssistBotConf)):
            logging.info(
                f"Reading WordPress Post cache: {ApplicationPath.WP_POSTS_CACHE.value}"
            )
            self._site: WordPress = WordPress(
                self._general_config.fq_domain_name,
                wp_auth.user,
                wp_auth.app_password,
                ApplicationPath.WP_POSTS_CACHE.value,
                unique_logging_session=False,
            )
        else:
            logging.info(
                f"Reading WordPress Photos Post cache: {ApplicationPath.WP_PHOTOS_CACHE.value}"
            )
            self._site: WordPress = WordPress(
                self._general_config.fq_domain_name,
                wp_auth.user,
                wp_auth.app_password,
                ApplicationPath.WP_PHOTOS_CACHE.value,
                use_photo_support=True,
                unique_logging_session=False,
            )

    def _do_wp_sync(self):
        with self._console.status(
            f"[{self._action_style}] Updating WordPress Local Cache... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
            spinner="bouncingBall",
        ):
            self._site.cache_sync()

    def _do_content_select_db_match(self):
        from workflows.utils.databases import content_select_db_match

        partners = [partner.strip() for partner in self._bot_config.partners.split(",")]
        _, cur_dump, partner_db_name, partner_indx = content_select_db_match(
            partners,
            self._bot_config.content_hint,
            dir=ApplicationPath.ARTIFACTS.value,
            parent=self._parent,
        )
        self._partner = partners[partner_indx]
        self._partner_db_name = partner_db_name
        self._cursor = cur_dump
        logging.info(
            f"Matched {partner_db_name} for {self._partner} index {partner_indx}"
        )

    def _select_guardian(self):
        from workflows.utils.filtering import select_guard

        select_guard(self._partner_db_name, self._partner)
        logging.info("Select guard cleared...")

    def _define_query(self):
        from rich.prompt import Prompt, Confirm
        from workflows.utils.databases import query_modifier

        if Confirm.ask(
            f"[{self._attention_style}]Use stored database query?[/{self._attention_style}]"
        ):
            logging.info(f"Using stored database query {self._query}")
        else:
            self._query = Prompt.ask(
                f"[{self._prompt_style}]Enter database query[/{self._prompt_style}]"
            )
            if Confirm.ask(
                f"[{self._attention_style}]Store this query for future sessions?[/{self._attention_style}]"
            ):
                modified = query_modifier(self._query, self._bot_config)
                if modified:
                    logging.info(f"Stored custom query {self._query}")
                else:
                    logging.info("Query not modified/stored")
            else:
                logging.info(f"Using custom database query {self._query}")

    def _run_query(self):
        from sqlite3 import OperationalError
        from core.utils.data_access import fetch_data_sql
        from core.exceptions import InvalidSQLConfig

        try:
            if self._query is None:
                self._query = self._bot_config.sql_query
            self._query_result: List[Tuple[str, ...]] = fetch_data_sql(
                self._query, self._cursor
            )
            logging.info(
                f"{len(self._query_result)} elements found in database {self._partner_db_name}"
            )
        except OperationalError as oerr:
            logging.error(
                f"Error while fetching data from SQL: {oerr!r} likely a configuration issue for partner {self._partner}."
            )
            raise InvalidSQLConfig(partner=self._partner)

    def _thumbnails_dir_setup(self):
        from tempfile import TemporaryDirectory
        from core.utils.file_system import exists_ok

        self._thumbnails_dir = TemporaryDirectory(
            prefix="thumbs", dir=exists_ok(ApplicationPath.TEMPORARY)
        )
        logging.info(
            f"Created {self._thumbnails_dir.name} for thumbnail temporary storage"
        )

    def _filter_published(self):
        from workflows.utils.filtering import filter_published

        filter_videos = lambda: filter_published(self._query_result, self._site)  # noqa: E731
        if self._interactive:
            with self._console.status(
                f"[{self._action_style}] Filtering ... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
                spinner="bouncingBall",
            ):
                self._ready_posts = filter_videos()
        else:
            self._ready_posts = filter_videos()

        self._total_ready = len(self._ready_posts)
        logging.info(f"Filtered {len(self._query_result) - self._total_ready} posts")
        logging.info(
            f"{self._total_ready} elements to be published in database {self._partner_db_name}"
        )

    def _filter_embeds(self):
        from workflows.utils.filtering import filter_published_embeds

        with self._console.status(
            f"[{self._action_style}] Filtering ... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
            spinner="bouncingBall",
        ):
            self._ready_posts = filter_published_embeds(
                self._site, self._query_result, self._cursor
            )
            self._total_ready = len(self._ready_posts)
        logging.info(
            f"{self._total_ready} elements found in database {self._partner_db_name}"
        )

    def _init_run(self):
        if os.name == "posix":
            import readline  # noqa: F401

        self._logging_setup()
        self._console_setup()

        with self._console.status(
            f"[{self._action_style}] Initializing components... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
            spinner="bouncingBall",
        ):
            self._refresh_token_setup()
            self._wp_setup()
        self._do_wp_sync()
        self._do_content_select_db_match()
        self._select_guardian()
        self._define_query()
        self._run_query()
        self._thumbnails_dir_setup()

    @abstractmethod
    def run(self) -> None:
        pass
