"""
Gallery Selection and Upload Module

This module facilitates the process of selecting and uploading image galleries to WordPress.
It automates several key steps:

1. Fetching galleries from a database that haven't been published yet
2. Fetching ZIP archives containing image sets based on download links
3. Extracting images to a temporary location for processing
4. Uploading image sets to WordPress with appropriate metadata
5. Creating WordPress posts with the uploaded images
6. Managing social sharing options

The module provides an interactive console interface that guides users through
the selection and uploading process. It allows filtering of content based on
relevancy to existing site content and handles error conditions gracefully.

The main function `gallery_upload_pilot()` orchestrates the entire workflow,
while supporting functions and command-line options provide flexibility in
execution parameters such as using different web drivers and controlling
headless browser operation.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import logging
import os.path
import tempfile
import time


# Third-party modules
import pyclip
from requests.exceptions import ConnectionError, SSLError

import core.utils.system_shell

# Local implementations
from tools.workflows_api import (
    ConsoleStyle,
    filter_published,
    get_tag_ids,
    filter_relevant,
    make_photos_post_payload,
    fetch_zip,
    extract_zip,
    upload_image_set,
    terminate_loop_logging,
    pilot_warm_up,
    iter_session_print,
    social_sharing_controller,
)

from core import helpers, gallery_select_conf, wp_auth

# Imported for typing purposes
from core.config_mgr import WPAuth, GallerySelectConf
from integrations import wordpress_api, WPEndpoints


def gallery_upload_pilot(
    relevancy_on: bool = False,
    gecko: bool = False,
    headless: bool = False,
    parent: bool = False,
    wp_admin_auth: WPAuth = wp_auth(),
    wp_endpoints: WPEndpoints = WPEndpoints,
    gallery_sel_conf: GallerySelectConf = gallery_select_conf(),
) -> None:
    """Control the entire execution of the gallery upload process.
    This ``gallery_upload_pilot`` function is a modification of ``video_upload_pilot``
    in the ``workflows.content_select`` module in the same package.
    It includes modifications that are necessary to deal with extra steps and automation:

    Note: the function calls specialized units that have been implemented for each responsibility,
    ``gallery_upload_pilot`` is just a job control that puts it all together, just like other like it in this package.

    1. Fetch a ``.zip`` archive with a download link provided by the database
    2. Locate, extract that .zip file into a temporary location, and dispose of the archive file.
    3. Upload a set of images to WordPress with appropriate metadata and clean successful uploads from the disk simultaneously.
    4. Build the payloads to create a post in WordPress once the image set has been successfully uploaded.

    If you want to know more about the flow control involved in this function, refer to the documentation
    for ``video_upload_pilot`` in the ``workflows.content_select`` module as there is a more detailed
    breakdown of the process.

    :param relevancy_on: ``bool`` ``True`` to enable the relevancy algorithm (experimental). Default ``False``
    :param gecko: ``bool`` ``True`` if you want to use the Gecko webdriver. Default ``False`` (Chrome)
    :param headless: ``bool`` ``True`` will enable the ``headless`` of the webdriver. For more information on this refer to the ``fetch_zip`` documentation on this module.
    :param parent: ``bool`` ``True`` if you are operating in the parent directory. Default ``False``
    :param wp_admin_auth: ``WPAuth`` object with information about you WP site.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :param gallery_sel_conf: ``GallerySelectConf`` object with configuration options for this module.
    :return: ``None``
    """
    time_start = time.time()

    (
        console,
        partner,
        not_published,
        all_galleries,
        wp_posts_f,
        wp_photos_f,
        thumbnails_dir,
    ) = pilot_warm_up(gallery_sel_conf, wp_admin_auth, parent=parent)

    # Prints out at the end of the uploading session.
    galleries_uploaded: int = 0

    if relevancy_on:
        logging.info("Relevancy algorithm on...")
        not_published_yet = filter_relevant(all_galleries, wp_posts_f, wp_photos_f)
    else:
        # In theory, this will work "sometimes" since I modify some of the
        # gallery names to reflect the queries we rank for on Google.
        # I don't use it as it is still experimental.
        logging.info("Relevancy algorithm off...")
        not_published_yet = filter_published(all_galleries, wp_photos_f)

    # You can keep on getting sets until this variable is equal to one.
    total_elems: int = len(not_published_yet)
    logging.info(f"Detected {total_elems} to be published")

    core.utils.system_shell.clean_console()

    iter_session_print(console, total_elems, partner=partner)
    time.sleep(2)
    temp_dir = tempfile.TemporaryDirectory(dir=".")
    logging.info(f"Created {temp_dir.name} for temporary file download & extraction")
    thumbnails_dir = tempfile.TemporaryDirectory(prefix="thumbs", dir=".")
    logging.info(f"Created {thumbnails_dir.name} for thumbnail temporary storage")

    user_default_style = ConsoleStyle.TEXT_STYLE_DEFAULT.value
    user_program_action = ConsoleStyle.TEXT_STYLE_ACTION.value
    user_prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
    user_program_special_style = ConsoleStyle.TEXT_STYLE_SPECIAL_PROMPT.value

    for num, photo in enumerate(not_published_yet):
        (title, *fields) = photo
        logging.info(f"Displaying on iteration {num} data: {photo}")
        date: str = fields[0]
        download_url: str = fields[1]
        partner_name: str = partner

        core.utils.system_shell.clean_console()

        iter_session_print(console, galleries_uploaded, elem_num=num)
        console.print(title, style=user_default_style)
        console.print(f"Date: {date}", style=user_default_style)
        console.print(f"Download URL: \n{download_url}", style=user_default_style)
        add_post: str | bool = console.input(
            f"[{user_prompt_style}]\nAdd set to WP? -> Y/N/ENTER to review next set: [/{user_prompt_style}]\n"
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {num} for processing")
            add_post: bool = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further interaction with the bot")
            temp_dir.cleanup()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            terminate_loop_logging(
                console,
                num,
                total_elems,
                galleries_uploaded,
                (h, mins, secs),
                exhausted=False,
            )
        else:
            if num < total_elems - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                temp_dir.cleanup()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    galleries_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        if add_post:
            console.print("\n--> Making payload...", style=user_program_action)
            tag_list: list[int] = get_tag_ids(wp_photos_f, [partner_name], "photos")
            payload: dict[str, str | int] = make_photos_post_payload(
                wp_admin_auth.default_status,
                title,
                partner_name,
                tag_list,
                reverse_slug=gallery_sel_conf.reverse_slug,
            )

            logging.info(f"Generated payload: {payload}")

            try:
                fetch_zip(
                    temp_dir.name,
                    download_url,
                    parent=parent,
                    gecko=gecko,
                    headless=headless,
                )
                extract_zip(temp_dir.name, thumbnails_dir.name)

                upload_image_set(
                    gallery_sel_conf.pic_fallback, thumbnails_dir.name, title
                )

                # Env variable set at make_photos_post_payload() in workflows_api.py
                wp_slug = os.environ.get("SET_SLUG")
                logging.info(f"WP Slug - Selected: {wp_slug}")

                console.print(
                    "--> Creating set on WordPress", style=user_program_action
                )

                push_post = wordpress_api.wp_post_create([wp_endpoints.photos], payload)
                logging.info(wp_push_msg := f"WordPress post push status: {push_post}")
                console.print(wp_push_msg, style=user_program_action)

                pyclip.detect_clipboard()
                # This is the main tag for galleries
                pyclip.copy(partner.lower())
                pyclip.copy(title)
                console.print(
                    "--> Check the set and paste your focus phrase on WP.",
                    style=user_program_special_style,
                )
                social_sharing_controller(console, title, wp_slug, gallery_sel_conf)
                galleries_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {e!r} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                wp_slug = os.environ.get("SET_SLUG")
                is_published = (
                    True if os.environ.get("LATEST_POST") == wp_slug else False
                )
                console.print(
                    "* There was a connection error while processing this set. Check the logs for details! *",
                    style="bold red",
                )
                console.print(
                    f"Set {os.environ.get('SET_SLUG')} was {'' if is_published else 'NOT'} published!",
                    style="bold red",
                )
                if console.input(
                    "[bold yellow]\nDo you want to continue? Y/ENTER to exit: [/bold yellow]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {e!r}")

                    if is_published:
                        galleries_uploaded += 1

                    continue
                else:
                    logging.info(f"User declined after catching {e!r}")

                    if is_published:
                        galleries_uploaded += 1

                    temp_dir.cleanup()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        galleries_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
            if num < total_elems - 1:
                next_post = console.input(
                    f"[{user_prompt_style}]\nNext set? -> N/ENTER to review next set: [/{user_prompt_style}]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    temp_dir.cleanup()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        galleries_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    pyclip.detect_clipboard()
                    pyclip.clear()
            else:
                temp_dir.cleanup()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    galleries_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        else:
            temp_dir.cleanup()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            terminate_loop_logging(
                console,
                num,
                total_elems,
                galleries_uploaded,
                (h, mins, secs),
                exhausted=True,
            )


def cli_args_group():
    arg_parser = argparse.ArgumentParser(
        description="Gallery Select Assistant - Behaviour Tweaks"
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        default=False,
        help="""Define if database and file search happens in the parent directory.
                                                This argument also affects:
                                                1. Thumbnail search
                                                2. HotSync caching
                                                3. Cache cleaning
                                                The default is set to false, so if you execute this file as a module,
                                                you may not want to enable it because this is treated as a package.
                                                If you are experiencing issues with the location of your thumbnails and relative
                                                references, this is a good place to start.""",
    )

    arg_parser.add_argument(
        "--gecko",
        action="store_true",
        help="Use the gecko webdriver for the browser automation steps.",
    )

    arg_parser.add_argument(
        "--relevancy",
        action="store_true",
        help="Activate relevancy algorithm (experimental)",
    )

    arg_parser.add_argument(
        "--headless",
        action="store_true",
        help="Enable headless webdriver execution. Compatibility is experimental with this module.",
    )

    return arg_parser.parse_args()


def main(*args, **kwargs):
    try:
        args_cli = cli_args_group()
        relevancy_on = args_cli.relevancy
        gecko = args_cli.gecko
        parent = args_cli.parent
        gallery_upload_pilot(
            *args, relevancy_on=relevancy_on, gecko=gecko, parent=parent
        )
    except KeyboardInterrupt:
        logging.critical("KeyboardInterrupt exception detected")
        logging.info("Cleaning clipboard and temporary directories. Quitting...")
        print("Goodbye! ಠ‿↼")
        pyclip.detect_clipboard()
        pyclip.clear()
        logging.shutdown()
        # When quit is called, temp dirs will be automatically cleaned.
        quit()


if __name__ == "__main__":
    main()
