"""
MongerCash AI Assistant for WordPress

This module provides a command-line interface to an AI-powered workflow for uploading
content to WordPress. Similar in function to `mcash_assistant`, it automates the
process of publishing video and gallery content from the MongerCash database.

It orchestrates the entire workflow, from fetching content metadata to publishing
the final post. The main `video_upload_pilot` function coordinates tasks such as
file management, metadata processing, thumbnail generation, and communicating
with the WordPress API.

This script is intended to be used with content databases created by the
`update_mcash_chain.py` script, streamlining the content pipeline for
MongerCash partners.

Key Features:
  - Command-line interface for flexible execution.
  - AI-powered workflow for intelligent content handling.
  - Integration with WordPress API for creating and managing posts.
  - Automated processing for images and video thumbnails.
  - Handles content metadata, categories, and tags.
  - Support for social media sharing integrations.
  - Manages temporary files and clipboard for a smoother workflow.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import logging
import os
import random
import time
from argparse import Namespace
from pathlib import Path


# Third-party modules
import pyclip
from requests.exceptions import SSLError, ConnectionError

# Local implementations
from core.utils.helpers import get_duration
from core.config.config_factories import (
    mcash_content_bot_conf_factory,
    image_config_factory,
    general_config_factory,
)
from core.models.config_model import MCashContentBotConf
from core.utils.system_shell import clean_console
from core.utils.file_system import clean_filename
from core.utils.strings import split_char

from ai_core.ai_workflows import ai_video_attrs
from ai_core.ai_client_mgr import load_llm_model
from ai_core.config import ai_config as ai
from workflows.utils.checkers import model_checker, tag_checker_print, get_tag_ids
from workflows.utils.parsing import asset_parser
from workflows.utils.social import social_sharing_controller
from workflows.utils.builders import make_payload, make_img_payload
from workflows.utils.strings import clean_partner_tag
from workflows.utils.file_handling import fetch_thumbnail, fetch_thumbnail_file
from workflows.utils.initialise import pilot_warm_up
from workflows.utils.logging import (
    ConsoleStyle,
    terminate_loop_logging,
    iter_session_print,
)


def video_upload_pilot(
    parent: bool = False,
) -> None:
    """Coordinate execution of all functions that interact with the video upload process.
    In other words, this function gives continuity to what ``workflows.update_mcash_chain`` does with
    the data processing and normalisation. Of course, that is just one way to put it since all other
    members in the module undertake a fraction of work, thus, each output is received and made meaningful here.

    :param parent: ``True`` if you want to locate relevant files in the parent directory. Default False
    :return: ``None``
    """
    time_start = time.time()
    cs_config: MCashContentBotConf = mcash_content_bot_conf_factory()
    console, partner, not_published, wp_site, thumbnails_dir = pilot_warm_up(
        cs_config, parent=parent
    )

    clean_console()

    with console.status(
        "Loading Large Language Model... ᕙ(▀̿ĺ̯▀̿ ̿)ᕗ",
        spinner="bouncingBall",
        spinner_style=ConsoleStyle.TEXT_STYLE_ACTION.value,
    ):
        llm, _ = load_llm_model()

    logging.info(f"Loaded LLM: {ai.MODEL_ID} Successfully")
    # Prints out at the end of the uploading session.
    videos_uploaded = 0
    banners = asset_parser(cs_config, partner)

    not_published_yet: list[tuple[str, ...]] = not_published

    # You can keep on getting posts until this variable is equal to one.
    total_elems: int = len(not_published_yet)
    logging.info(f"Detected {total_elems} to be published for {partner}")

    clean_console()

    iter_session_print(console, total_elems, partner=partner)
    time.sleep(2)

    for num, vid in enumerate(not_published_yet):
        (title, *fields) = vid
        logging.info(f"Displaying on iteration {num} data: {vid}")
        description = fields[0]
        models = fields[1]
        tags = fields[2]
        date = fields[3]
        duration = fields[4]
        source_url = fields[5]
        thumbnail_url = fields[6]
        tracking_url = fields[7]
        partner_name = partner

        clean_console()
        iter_session_print(console, videos_uploaded, elem_num=num)

        style_fields = ConsoleStyle.TEXT_STYLE_DEFAULT.value
        console.print(title, style=style_fields)
        console.print(description, style=style_fields)
        console.print(f"Duration: {duration}", style=style_fields)
        console.print(f"Tags: {tags}", style=style_fields)
        console.print(f"Models: {models}", style=style_fields)
        console.print(f"Date: {date}", style=style_fields)
        console.print(f"Thumbnail URL: {thumbnail_url}", style=style_fields)
        console.print(f"Source URL: {source_url}", style=style_fields)

        prompt_style: str = ConsoleStyle.TEXT_STYLE_PROMPT.value
        add_post = console.input(
            f"\n[{prompt_style}]Add post to WP? -> Y/N/ENTER to review next post: [/{prompt_style}]\n",
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {num} for processing")
            add_post = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further activity with the bot")
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = get_duration(time_end - time_start)
            terminate_loop_logging(
                console,
                num,
                total_elems,
                videos_uploaded,
                (h, mins, secs),
                exhausted=False,
            )
            llm.unload()
        else:
            if num < total_elems - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = get_duration(time_end - time_start)
                terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
                llm.unload()
        # In rare occasions, the ``tags`` is None and the real tags are placed in the ``models`` variable
        # this special handling prevents crashes
        if not tags:
            tags, models = models, tags

        thumbnail_path, thumb_fetch_status = fetch_thumbnail_file(
            thumbnails_dir.name, thumbnail_url
        )

        if add_post:
            with console.status("Optimizing post ... ᕙ(▀̿ĺ̯▀̿ ̿)ᕗ", spinner="point"):
                if thumb_fetch_status == 200:
                    (
                        alt_text_ai,
                        caption_ai,
                        description_ai,
                        category_ai,
                        slug_ai,
                        tags_ai,
                    ) = ai_video_attrs(
                        Path(thumbnail_path), title, description, tags, llm
                    )

            os.remove(thumbnail_path)
            wp_slug = slug_ai
            logging.info(f"WP Slug - Selected by LLM {ai.MODEL_ID}: {wp_slug}")
            tag_prep: list[str] = [tag.strip() for tag in tags.split(",")]

            for ai_tag in tags_ai:
                tag_prep.append(ai_tag)

            # Making sure that the partner tag does not have apostrophes
            tag_prep.append(clean_partner_tag(partner.lower()))
            tag_ints = tag_checker_print(console, wp_site, tag_prep)

            try:
                model_delim = models.split(
                    spl_ch if (spl_ch := split_char(models)) != " " else "-1"
                )
                model_prep = list(map(lambda model: model.strip(), model_delim))
            except AttributeError:
                model_prep = []

            calling_models: list[int] = model_checker(wp_site, model_prep)

            # NaiveBayes/MaxEnt classification for titles, descriptions, and tags
            categ_ids: list[int] = get_tag_ids(
                wp_site, [category_ai], preset="categories"
            )
            logging.info(
                f"WordPress API matched category ID: {categ_ids} for category: {category_ai}"
            )

            program_action_style: str = ConsoleStyle.TEXT_STYLE_ACTION.value
            program_warning_style: str = ConsoleStyle.TEXT_STYLE_WARN.value

            console.print("\n--> Making payload...", style=program_action_style)
            payload = make_payload(
                wp_slug,
                general_config_factory().default_status,
                title,
                description if not description_ai else description_ai,
                tracking_url,
                random.choice(banners),
                partner_name,
                tag_ints,
                calling_models,
                categs=categ_ids,
            )
            logging.info(f"Generated payload: {payload}")
            console.print("--> Fetching thumbnail...", style=program_action_style)

            image_config = image_config_factory()
            # Check whether ImageMagick conversion has been enabled in config.
            pic_format = (
                image_config.pic_format
                if image_config.imagick
                else image_config.pic_fallback
            )
            thumbnail = clean_filename(wp_slug, pic_format)
            logging.info(f"Thumbnail name: {thumbnail}")

            try:
                fetch_thumbnail(thumbnails_dir.name, wp_slug, thumbnail_url)
                console.print(
                    f"--> Stored thumbnail {thumbnail} in cache folder {os.path.relpath(thumbnails_dir.name)}",
                    style=program_action_style,
                )
                console.print(
                    "--> Uploading thumbnail to WordPress Media...",
                    style=program_action_style,
                )
                console.print(
                    "--> Adding image attributes on WordPress...",
                    style=program_action_style,
                )
                img_attrs: dict[str, str] = make_img_payload(
                    title,
                    description,
                    flat_payload=(alt_text_ai, caption_ai, description_ai),
                )
                upload_img: int = wp_site.upload_image(
                    os.path.join(thumbnails_dir.name, thumbnail),
                    img_attrs,
                )
                logging.info(f"Image Attrs: {img_attrs}")

                # Sometimes, the function fetch_thumbnail fetches an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is the case.
                # More information in integrations.wordpress_api.upload_thumbnail docs

                if upload_img == 500:
                    logging.warning("Defective thumbnail - Bot abandoned current flow.")
                    console.print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually.",
                        style=program_warning_style,
                    )
                    console.print(
                        "--> Proceeding to the next post...\n",
                        style=program_action_style,
                    )
                    continue
                elif upload_img == (200 or 201):
                    os.remove(
                        removed_img := os.path.join(thumbnails_dir.name, thumbnail)
                    )
                    logging.info(f"Uploaded and removed: {removed_img}")

                console.print(
                    f"--> WordPress Media upload status code: {upload_img}",
                    style=program_action_style,
                )
                console.print(
                    "--> Creating post on WordPress", style=program_action_style
                )

                push_post: int = wp_site.post_create(payload)
                logging.info(f"WordPress post push status: {push_post}")
                console.print(
                    f"--> WordPress status code: {push_post}",
                    style=program_action_style,
                )

                pyclip.detect_clipboard()
                pyclip.copy(source_url)
                pyclip.copy(title)
                console.print(
                    "--> Check the post and paste all you need from your clipboard.",
                    style=program_action_style,
                )
                social_sharing_controller(
                    console, description, wp_slug, cs_config, wp_site
                )
                videos_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {e!r} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this post. Check the logs for more details...*",
                    style=program_warning_style,
                )

                is_published = (
                    True if wp_slug == os.environ.get("LATEST_POST") else False
                )
                console.print(
                    f"Post {wp_slug} was {'' if is_published else 'NOT'} published!",
                    style=program_warning_style,
                )
                if console.input(
                    f"\n[{prompt_style}] Do you want to continue? Y/ENTER to exit: [{prompt_style}]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {e!r}")

                    if is_published:
                        videos_uploaded += 1

                    continue
                else:
                    logging.info(f"User declined after catching {e!r}")

                    if is_published:
                        videos_uploaded += 1

                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = get_duration(time_end - time_start)
                    terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                    llm.unload()
            if num < total_elems - 1:
                next_post = console.input(
                    f"[{prompt_style}]\nNext post? -> N/ENTER to review next post: [/{prompt_style}]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    logging.info("User declined further activity with the bot")
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = get_duration(time_end - time_start)
                    terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                    llm.unload()
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    pyclip.detect_clipboard()
                    pyclip.clear()
            else:
                time_end = time.time()
                h, mins, secs = get_duration(time_end - time_start)
                terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
                llm.unload()


def bot_cli_args() -> Namespace:
    arg_parser = argparse.ArgumentParser(
        description="Content Select Assistant - Behaviour Tweaks"
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        help="""Define if database and file search happens in the parent directory.
                                        This argument also affects:
                                        1. Thumbnail search
                                        2. HotSync caching
                                        3. Cache cleaning
                                        The default is set to false, so if you execute this file as a module,
                                        you may not want to enable it because this is treated as a package.""",
    )

    return arg_parser.parse_args()


def main():
    try:
        if os.name == "posix":
            import readline  # noqa: F401
        cli_args = bot_cli_args()
        video_upload_pilot(parent=cli_args.parent)
    except KeyboardInterrupt:
        logging.critical("KeyboardInterrupt exception detected")
        logging.info("Cleaning clipboard and temporary directories. Quitting...")
        print("Goodbye! ಠ‿↼")
        pyclip.detect_clipboard()
        pyclip.clear()
        # When ``exit`` is called, temp dirs will be automatically cleaned.
        logging.shutdown()
        exit(0)


if __name__ == "__main__":
    main()
