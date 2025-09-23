"""
Workflows Initialisation module

This module is responsible for initialising the workflows by performing
common operations such as logging setup, database selection, and WordPress post-handling that
must take place in all workflow bots.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os

import tempfile
from sqlite3 import OperationalError
from typing import List, Tuple, Union

# Third-party imports
import urllib3.exceptions
from rich.console import Console

# Local imports
from core.config.config_factories import general_config_factory, social_config_factory
from core.exceptions.data_access_exceptions import (
    InvalidSQLConfig,
    UnableToConnectError,
)
from core.models.config_model import (
    MCashContentBotConf,
    MCashGalleryBotConf,
    EmbedAssistBotConf,
)
from core.models.file_system import ApplicationPath
from core.models.secret_model import SecretType, WPSecrets
from core.utils.data_access import fetch_data_sql
from core.utils.file_system import logging_setup, exists_ok
from core.utils.secret_handler import SecretHandler
from core.utils.system_shell import clean_console
from integrations import x_api, XEndpoints
from wordpress import WordPress
from workflows.utils.databases import content_select_db_match
from workflows.utils.filtering import filter_published, select_guard
from workflows.utils.logging import ConsoleStyle


def pilot_warm_up(
    cs_config: Union[MCashContentBotConf, MCashGalleryBotConf, EmbedAssistBotConf],
    parent: bool = False,
):
    """
    Performs initialization operations for processing content selection, database operations,
    and WordPress post handling with the provided configuration and authentication.

    :param cs_config: ``MCashContentBotConf | MCashGalleryBotConf | EmbedAssistBotConf`` Object
                      representing the configuration for the content selection process.
    :param parent: ``bool`` optional. Flag indicating whether to use parent-level matching for
                  database content selection. Defaults to False.
    :return: ``None``
    :raises: ``UnableToConnectError`` Raised when the connection to the server fails after exceeding
            the maximum number of retries.
    """
    general_config = general_config_factory()
    try:
        if general_config.enable_logging:
            logging_setup("logs", __file__)
            logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}")

        console = Console()

        clean_console()

        partners: List[str] = [
            partner.strip() for partner in cs_config.partners.split(",")
        ]

        # Replacing this with the above line
        # partners: list[str] = list(
        #     map(lambda p: p.strip(), cs_config.partners.split(","))
        # )

        status_style = ConsoleStyle.TEXT_STYLE_ACTION.value
        with console.status(
            f"[{status_style}] Warming up... [blink]┌(◎_◎)┘[/blink] [/{status_style}]\n",
            spinner="aesthetic",
        ):
            if social_config_factory().x_posting:
                x_api.refresh_flow(
                    SecretHandler().get_secret(SecretType.X_REFRESH_TOKEN)[0],
                    XEndpoints(),
                )

        logging.info(f"Loading partners variable: {partners}")

        wp_auth: WPSecrets = SecretHandler().get_secret(SecretType.WP_APP_PASSWORD)[0]

        logging.info(f"Loaded WP Auth: {wp_auth}")

        with console.status(
            f"[{status_style}] Loading WordPress Engine... [blink]┌(◎_◎)┘[/blink] [/{status_style}]\n",
            spinner="aesthetic",
        ):
            if isinstance(cs_config, (MCashContentBotConf, EmbedAssistBotConf)):
                logging.info(
                    f"Reading WordPress Post cache: {ApplicationPath.WP_POSTS_CACHE.value}"
                )
                wp_site: WordPress = WordPress(
                    general_config.fq_domain_name,
                    wp_auth.user,
                    wp_auth.app_password,
                    ApplicationPath.WP_POSTS_CACHE.value,
                )
            else:
                logging.info(
                    f"Reading WordPress Photos Post cache: {ApplicationPath.WP_PHOTOS_CACHE.value}"
                )
                wp_site: WordPress = WordPress(
                    general_config.fq_domain_name,
                    wp_auth.user,
                    wp_auth.app_password,
                    ApplicationPath.WP_PHOTOS_CACHE.value,
                    use_photo_support=True,
                )

        with console.status(
            f"[{status_style}] Updating WordPress Local Cache... [blink]┌(◎_◎)┘[/blink] [/{status_style}]\n",
            spinner="bouncingBall",
        ):
            wp_site.cache_sync()

        _, cur_dump, partner_db_name, partner_indx = content_select_db_match(
            partners,
            cs_config.content_hint,
            dir=ApplicationPath.ARTIFACTS.value,
            parent=parent,
        )

        partner = partners[partner_indx]
        select_guard(partner_db_name, partner)
        logging.info("Select guard cleared...")

        logging.info(f"Matched {partner_db_name} for {partner} index {partner_indx}")

        try:
            all_vals: List[Tuple[str, ...]] = fetch_data_sql(
                cs_config.sql_query, cur_dump
            )
        except OperationalError as oerr:
            logging.error(
                f"Error while fetching data from SQL: {oerr!r} likely a configuration issue for partner {partner}."
            )
            raise InvalidSQLConfig(partner=partner)

        logging.info(f"{len(all_vals)} elements found in database {partner_db_name}")

        thumbnails_dir = tempfile.TemporaryDirectory(
            prefix="thumbs", dir=exists_ok(ApplicationPath.TEMPORARY)
        )
        logging.info(f"Created {thumbnails_dir.name} for thumbnail temporary storage")

        with console.status(
            f"[{status_style}] Filtering ... [blink]┌(◎_◎)┘[/blink] [/{status_style}]\n",
            spinner="bouncingBall",
        ):
            not_published: List[Tuple[str, ...]] = filter_published(all_vals, wp_site)

        if cs_config.__class__.__name__ == "EmbedAssistBotConf":
            return console, partner, not_published, wp_site, thumbnails_dir, cur_dump
        elif cs_config.__class__.__name__ == "MCashContentBotConf":
            return console, partner, not_published, wp_site, thumbnails_dir
        else:
            wp_photos_site: WordPress = WordPress(
                general_config.fq_domain_name,
                wp_auth.user,
                wp_auth.app_password,
                ApplicationPath.WP_PHOTOS_CACHE.value,
                use_photo_support=True,
            )
            logging.info(
                f"Reading WordPress Photo Posts cache: {ApplicationPath.WP_PHOTOS_CACHE.value}"
            )
            return (
                console,
                partner,
                not_published,
                all_vals,
                wp_site,
                wp_photos_site,
                thumbnails_dir,
            )

    except urllib3.exceptions.MaxRetryError:
        raise UnableToConnectError
