"""
Embedding Assistant Module

This module provides functionality to assist with video embedding tasks from Asian
adult content providers. It automates the process of adding video posts to a WordPress
site by handling embedding information, thumbnails, and metadata.

The main function `embedding_pilot()` guides the user through an interactive session to:
1. Select videos from a database that haven't been published yet
2. View and manage video metadata (title, description, duration, etc.)
3. Generate WordPress slugs with various patterns
4. Process tags, models, and categories with smart classification
5. Upload thumbnails to WordPress Media
6. Create posts with embedded video content
7. Handle social sharing options

The module uses a console-based interface for user interaction and provides
detailed logging of operations.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import re
import time

from typing import Optional, List

# Third-party modules
import pyclip
import requests
from requests.exceptions import SSLError, ConnectionError

# Local implementations

from workflows.interfaces import EmbedsMultiSchema
from workflows.builders import (
    WorkflowSlugBuilder,
    WorkflowPostPayloadBuilder,
    WorkflowMediaPayload,
)
from workflows.utils.strings import transform_partner_iframe
from workflows.utils.file_handling import fetch_thumbnail
from workflows.utils.initialise import pilot_warm_up
from workflows.utils.selectors import slug_getter, pick_classifier
from workflows.utils.checkers import tag_checker_print, model_checker
from workflows.utils.social import social_sharing_controller
from workflows.utils.logging import (
    ConsoleStyle,
    iter_session_print,
    terminate_loop_logging,
)

from core.utils.system_shell import clean_console
from core.utils.helpers import get_duration
from core.utils.file_system import clean_filename
from core.config.config_factories import (
    vid_embed_bot_conf_factory,
    general_config_factory,
    image_config_factory,
)

from postwizard_sdk.models.client_schema import (
    Ethnicity,
    ToggleField,
    Orientation,
    Production,
    HairColor,
)
from postwizard_sdk.builders import PostMetaNestedPayload
from postwizard_sdk.utils.operations import update_post_meta
from postwizard_sdk.utils.auth import PostWizardAuth


def embedding_pilot() -> None:
    """
    Assist the user in video embedding based on information originated from local
    implementations of Japanese adult content providers in the ``integrations`` package.

    :return: ``None``
    """
    time_start = time.time()

    embed_ast_conf = vid_embed_bot_conf_factory()
    general_config = general_config_factory()
    image_config = image_config_factory()

    console, partner, not_published, wp_site, thumbnails_dir, cur_dump = pilot_warm_up(
        embed_ast_conf
    )

    db_interface = EmbedsMultiSchema(cur_dump)
    videos_uploaded: int = 0

    # You can keep on getting posts until this variable is equal to one.
    total_elems: int = len(not_published)
    logging.info(f"Detected {total_elems} to be published for {partner}")

    clean_console()

    # Styles
    user_default = ConsoleStyle.TEXT_STYLE_DEFAULT.value
    user_default_bold = ConsoleStyle.TEXT_STYLE_ACTION.value
    user_attention = ConsoleStyle.TEXT_STYLE_ATTENTION.value
    user_warning = ConsoleStyle.TEXT_STYLE_WARN.value
    user_prompt = ConsoleStyle.TEXT_STYLE_PROMPT.value

    iter_session_print(console, total_elems, partner=partner)
    time.sleep(2)
    for num, vid in enumerate(not_published):
        db_interface.load_data_instance(vid)
        iteration = num
        logging.info(f"Displaying on iteration {iteration} data: {vid}")

        clean_console()

        iter_session_print(console, videos_uploaded, elem_num=num + 1)

        for field in db_interface.get_fields(keep_indx=True):
            num, fld = field
            if re.match(db_interface.SchemaRegEx.pat_duration, fld):
                hs, mins, secs = get_duration(int(db_interface.get_duration()))
                console.print(
                    f"{num + 1}. Duration: \n\tHours: [bold red]{hs}[/bold red] \n\tMinutes: [bold red]{mins}[/bold red] \n\tSeconds: [bold red]{secs}[/bold red]",
                    style=user_default_bold,
                )  # From seconds to hours to minutes
            else:
                console.print(f"{num}. {fld.title()}: {vid[num]}", style=user_default)

        add_post = console.input(
            f"[{user_prompt}]\nAdd post to WP? -> Y/N/ENTER to review next post: [/{user_prompt}]\n"
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {iteration} for processing")
            add_post = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further activity with the bot")
            cur_dump.close()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = get_duration(time_end - time_start)
            terminate_loop_logging(
                console,
                iteration,
                total_elems,
                videos_uploaded,
                (h, mins, secs),
                exhausted=False,
            )
        else:
            if iteration < total_elems - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: num={iteration} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                logging.info(
                    f"List exhausted. State: num={iteration} total_elems={total_elems}"
                )
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = get_duration(time_end - time_start)
                terminate_loop_logging(
                    console,
                    iteration,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        if add_post:
            # TODO: Introduce a config field in the config file and UI for this.
            transformed_iframe = transform_partner_iframe(
                db_interface.get_embed(), "https://video.whoresmen.com"
            )
            models = (
                girl
                if (girl := db_interface.get_models())
                else db_interface.get_pornstars()
            )

            slug_builder = WorkflowSlugBuilder(filter_words=["amp"])
            slugs = [
                f"{slug}" if (slug := db_interface.get_slug()) else "",
                slug_builder.title(db_interface.get_title()).build(),
                slug_builder.title(db_interface.get_title()).model(models).build(),
                slug_builder.title(db_interface.get_title())
                .studio(db_interface.get_studio())
                .build(),
                slug_builder.title(db_interface.get_title())
                .model(models)
                .partner(partner)
                .build(),
                slug_builder.title(db_interface.get_title())
                .model(models)
                .studio(db_interface.get_studio())
                .build(),
                slug_builder.title(db_interface.get_title())
                .model(models)
                .partner(partner)
                .content_type("video")
                .build(),
                slug_builder.title(db_interface.get_title())
                .model(models)
                .studio(db_interface.get_studio())
                .content_type("video")
                .build(),
                slug_builder.title(db_interface.get_title())
                .model(models)
                .content_type("video")
                .partner(partner)
                .build(),
                slug_builder.title(db_interface.get_title())
                .model(models)
                .content_type("video")
                .studio(db_interface.get_studio())
                .build(),
                slug_builder.partner(partner)
                .model(models)
                .title(db_interface.get_title())
                .content_type("video")
                .studio(db_interface.get_studio())
                .build(),
                slug_builder.model(models)
                .title(db_interface.get_title())
                .studio(db_interface.get_studio())
                .build(),
            ]

            wp_slug = slug_getter(
                console, list(dict.fromkeys([slug for slug in slugs if slug]))
            )

            logging.info(f"WP Slug - Selected: {wp_slug}")

            # Making sure there aren't spaces in tags and exclude the word
            # `asian` and `japanese` from tags since I want to make them more general.
            tag_prep: List[str] = re.split(
                "(?=\W)\S",
                categories
                if (categories := db_interface.get_categories())
                else db_interface.get_tags(),
            )

            tag_ints = tag_checker_print(console, wp_site, tag_prep, add_missing=True)

            models_field = (
                pornstars
                if (pornstars := db_interface.get_pornstars())
                else db_interface.get_models()
            )

            if models_field:
                models_prep = re.split(r"(?=\W)\S", models_field)
                model_ints: Optional[list[int]] = model_checker(
                    wp_site, models_prep, add_missing=True
                )
            else:
                model_ints = None

            # Video category NaiveBayes/MaxEnt Classifiers
            categ_ids = pick_classifier(
                console,
                wp_site,
                db_interface.get_title(),
                db_interface.get_description(),
                db_interface.get_tags()
                if db_interface.get_tags()
                else db_interface.get_categories(),
            )
            category = categ_ids

            console.print("\n--> Making payload...", style=user_default_bold)
            payload = WorkflowPostPayloadBuilder().payload_factory_simple(
                wp_slug,
                general_config.default_status,
                db_interface.get_title(),
                db_interface.get_description(),
                tag_ints,
                model_int_lst=model_ints,
                categs=category,
            )
            logging.info(f"Generated payload: {payload}")

            console.print("--> Fetching thumbnail...", style=user_default_bold)

            pic_format = (
                image_config.pic_format
                if image_config.imagick
                else image_config.pic_fallback
            )
            thumbnail = clean_filename(wp_slug, pic_format)
            logging.info(f"Thumbnail name: {thumbnail}")

            try:
                fetch_thumbnail(
                    thumbnails_dir.name,
                    wp_slug,
                    db_interface.get_thumbnail(),
                )
                console.print(
                    f"--> Stored thumbnail {thumbnail} in cache folder {os.path.relpath(thumbnails_dir.name)}",
                    style=user_default_bold,
                )
                console.print(
                    "--> Uploading thumbnail to WordPress Media...",
                    style=user_default_bold,
                )
                console.print(
                    "--> Adding image attributes on WordPress...",
                    style=user_default_bold,
                )
                img_attrs = WorkflowMediaPayload().payload_factory(
                    db_interface.get_title(), db_interface.get_description()
                )
                logging.info(f"Image Attrs: {img_attrs}")
                upload_img = wp_site.upload_image(
                    f"{os.path.join(thumbnails_dir.name, thumbnail)}", img_attrs
                )

                # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is the case.
                # More information in integrations.wordpress_api.upload_thumbnail docs
                if upload_img == 500:
                    logging.warning("Defective thumbnail - Bot abandoned current flow.")
                    console.print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually.",
                        style=user_warning,
                    )
                    console.print(
                        "--> Proceeding to the next post...\n", style=user_default_bold
                    )
                    continue
                elif upload_img == 200 or upload_img == 201:
                    os.remove(
                        removed_img := f"{os.path.join(thumbnails_dir.name, thumbnail)}"
                    )
                    logging.info(f"Uploaded and removed: {removed_img}")

                console.print(
                    f"--> WordPress Media upload status code: {upload_img}",
                    style=user_default_bold,
                )
                console.print("--> Creating post on WordPress", style=user_default_bold)

                push_post = wp_site.post_create(payload)
                logging.info(f"WordPress post push status: {push_post}")
                console.print(
                    f"--> WordPress status code: {push_post}", style=user_default_bold
                )

                logging.info(f"Detected media upload status: {upload_img}")
                h, mins, secs = get_duration(int(db_interface.get_duration()))
                new_post_id = wp_site.get_last_post()

                status_style = ConsoleStyle.TEXT_STYLE_ACTION.value
                with console.status(
                    f"[{status_style}] Creating post on WordPress... [blink]┌(◎_◎)┘[/blink] [/{status_style}]\n",
                    spinner="bouncingBall",
                ):
                    wp_site.publish_post(new_post_id.post_id)

                    post_meta_payload = (
                        PostMetaNestedPayload()
                        .ethnicity(
                            Ethnicity.INDIAN
                            if partner.startswith("Desi")
                            else Ethnicity.ASIAN
                        )
                        .hd(ToggleField.ON)
                        .orientation(Orientation.STRAIGHT)
                        .production(Production.PROFESSIONAL)
                        .hair_color(HairColor.BLACK)
                        .embed_code(transformed_iframe)
                        .hours(int(h))
                        .minutes(int(mins))
                        .seconds(int(secs))
                    )

                    update_post_embed = update_post_meta(
                        post_meta_payload, new_post_id.post_id, auto_thumb=True
                    )

                    retries = 0
                    while update_post_embed != requests.codes.ok:
                        logging.warning(
                            f"Post meta update status: {update_post_embed}. Retrying..."
                        )
                        PostWizardAuth.reset_auth()
                        update_post_embed = update_post_meta(
                            post_meta_payload, new_post_id.post_id, auto_thumb=True
                        )
                        if update_post_embed == requests.codes.ok:
                            logging.info(
                                f"Post meta update status: {update_post_embed} -> Success!"
                            )
                            break
                        retries += 1
                        time.sleep(5)
                        if retries == 3:
                            logging.warning(
                                f"Post meta update status: {update_post_embed}. Max retries reached."
                            )
                            console.print(
                                "* There an error while injecting the post meta fields, likely an authentication issue. Check the session logs for more details...*",
                                style=user_warning,
                            )
                            console.print(
                                "--> Rolling back and exiting...\n", style=user_warning
                            )
                            wp_site.post_delete(new_post_id.post_id)
                            raise KeyboardInterrupt

                logging.info(f"Sent payload to PostWizard: {post_meta_payload.build()}")
                logging.info(f"Post meta update status: {update_post_embed}")

                console.print(
                    "--> Post published successfully.",
                    style=user_attention,
                )
                post_meta_payload.clear()
                social_sharing_controller(
                    console,
                    db_interface.get_description(),
                    wp_slug,
                    embed_ast_conf,
                    wp_site,
                )
                videos_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {e!r} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this post. Check the logs for details. *",
                    style=user_warning,
                )
                is_published = (
                    True if wp_slug == os.environ.get("LATEST_POST") else False
                )
                console.print(
                    f"Post {wp_slug} was {'' if is_published else 'NOT'} published!",
                    style=user_warning,
                )
                if console.input(
                    f"\n[{user_prompt}] Do you want to continue? Y/ENTER to exit: [{user_prompt}]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {e!r}")

                    if is_published:
                        videos_uploaded += 1
                    continue

                else:
                    logging.info(f"User declined after catching {e!r}")

                    if is_published:
                        videos_uploaded += 1

                    console.print(
                        f"You have created {videos_uploaded} posts in this session!",
                        style=user_attention,
                    )
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = get_duration(time_end - time_start)
                    terminate_loop_logging(
                        console,
                        iteration,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                    logging.shutdown()
                    break
            if iteration < total_elems - 1:
                next_post = console.input(
                    f"[{user_prompt}]\nNext post? -> N/ENTER to review next post: [/{user_prompt}]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    logging.info("User declined further activity with the bot")
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = get_duration(time_end - time_start)
                    terminate_loop_logging(
                        console,
                        iteration,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    logging.info(
                        "Refreshing WordPress Local Cache and reloading site data to memory..."
                    )
                    clean_console()
                    status_style = ConsoleStyle.TEXT_STYLE_ACTION.value
                    with console.status(
                        f"[{status_style}] Refreshing WordPress Local Cache... [blink]┌(◎_◎)┘[/blink] [/{status_style}]\n",
                        spinner="bouncingBall",
                    ):
                        wp_site.cache_sync()
                    pyclip.detect_clipboard()
                    pyclip.clear()
            else:
                cur_dump.close()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = get_duration(time_end - time_start)
                terminate_loop_logging(
                    console,
                    iteration,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        else:
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = get_duration(time_end - time_start)
            terminate_loop_logging(
                console,
                iteration,
                total_elems,
                videos_uploaded,
                (h, mins, secs),
                exhausted=True,
            )


def main():
    try:
        if os.name == "posix":
            import readline  # noqa: F401

        embedding_pilot()
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
