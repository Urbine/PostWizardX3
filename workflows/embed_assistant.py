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

from typing import Optional

# Third-party modules
import pyclip
from requests.exceptions import SSLError, ConnectionError

# Local implementations
from core import helpers, embed_assist_conf, wp_auth, clean_filename
from integrations import wordpress_api, WPEndpoints

from . import workflows_api as workflows


def embedding_pilot(
    embed_ast_conf=embed_assist_conf(),
    wpauths=wp_auth(),
    wp_endpoints: WPEndpoints = WPEndpoints(),
) -> None:
    """
    Assist the user in video embedding from the information originated from local
    implementations of Japanese adult content providers in the ``integrations`` package.

    :param embed_ast_conf: ``EmbedAssistConf`` Object with configuration info for this bot.
    :param wpauths: ``WPAuth`` object that contains configuration of your site.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :return: ``None``
    """
    time_start = time.time()

    console, partner, not_published, wp_posts_f, thumbnails_dir, cur_dump = (
        workflows.pilot_warm_up(embed_ast_conf, wpauths)
    )

    db_interface = workflows.EmbedsMultiSchema(cur_dump)
    videos_uploaded: int = 0

    # You can keep on getting posts until this variable is equal to one.
    total_elems: int = len(not_published)
    logging.info(f"Detected {total_elems} to be published for {partner}")

    helpers.clean_console()

    # Styles
    user_default = workflows.ConsoleStyle.TEXT_STYLE_DEFAULT.value
    user_default_bold = workflows.ConsoleStyle.TEXT_STYLE_ACTION.value
    user_attention = workflows.ConsoleStyle.TEXT_STYLE_ATTENTION.value
    user_warning = workflows.ConsoleStyle.TEXT_STYLE_WARN.value
    user_prompt = workflows.ConsoleStyle.TEXT_STYLE_PROMPT.value

    workflows.iter_session_print(console, total_elems, partner=partner)
    time.sleep(2)
    for num, vid in enumerate(not_published):
        db_interface.load_data_instance(vid)
        logging.info(f"Displaying on iteration {num} data: {vid}")

        helpers.clean_console()

        workflows.iter_session_print(console, videos_uploaded, elem_num=num + 1)

        for field in db_interface.get_fields(keep_indx=True):
            num, fld = field
            if re.match(db_interface.SchemaRegEx.pat_duration, fld):
                hs, mins, secs = helpers.get_duration(int(db_interface.get_duration()))
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
            logging.info(f"User accepted video element {num} for processing")
            add_post = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further activity with the bot")
            cur_dump.close()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            workflows.terminate_loop_logging(
                console,
                num,
                total_elems,
                videos_uploaded,
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
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                workflows.terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        if add_post:
            models = (
                girl
                if (girl := db_interface.get_models())
                else db_interface.get_pornstars()
            )

            slugs = [
                f"{slug}" if (slug := db_interface.get_slug()) else "",
                workflows.make_slug(
                    partner, models, (title := db_interface.get_title()), "video"
                ),
                workflows.make_slug(partner, models, title, "video", reverse=True),
                workflows.make_slug(
                    partner, models, title, "video", studio=db_interface.get_studio()
                ),
                workflows.make_slug(
                    partner,
                    models,
                    title,
                    "video",
                    studio=db_interface.get_studio(),
                    partner_out=True,
                ),
                workflows.make_slug(
                    partner,
                    None,
                    title,
                    "video",
                    studio=db_interface.get_studio(),
                    partner_out=True,
                ),
            ]

            clean_slugs = list(filter(lambda sl: sl != "", slugs))

            wp_slug = workflows.slug_getter(console, clean_slugs)

            logging.info(f"WP Slug - Selected: {wp_slug}")

            # Making sure there aren't spaces in tags and exclude the word
            # `asian` and `japanese` from tags since I want to make them more general.
            tag_prep = workflows.filter_tags(
                categories
                if (categories := db_interface.get_categories())
                else db_interface.get_tags(),
                ["asian", "japanese"],
            )
            # Default tag per partner
            # TODO: Allow tag per partner config from config file, maybe a tuple. Refactor!!
            if partner == "abjav" or partner == "vjav":
                tag_prep.append("japanese")
            elif partner == "Desi Tube":
                tag_prep.append("indian")

            tag_ints = workflows.tag_checker_print(console, wp_posts_f, tag_prep)

            models_field = (
                pornstars
                if (pornstars := db_interface.get_pornstars())
                else db_interface.get_models()
            )

            if models_field:
                models_prep = workflows.filter_tags(models_field)
                model_ints: Optional[list[int]] = workflows.model_checker(
                    wp_posts_f, models_prep
                )
            else:
                model_ints = None

            # Video category NaiveBayes/MaxEnt Classifiers
            categ_ids = workflows.pick_classifier(
                console,
                wp_posts_f,
                db_interface.get_title(),
                db_interface.get_description(),
                db_interface.get_tags()
                if db_interface.get_tags()
                else db_interface.get_categories(),
            )
            category = categ_ids

            console.print("\n--> Making payload...", style=user_default_bold)
            payload = workflows.make_payload_simple(
                wp_slug,
                wpauths.default_status,
                title,
                db_interface.get_description(),
                tag_ints,
                model_int_lst=model_ints,
                categs=category,
            )
            logging.info(f"Generated payload: {payload}")

            console.print("--> Fetching thumbnail...", style=user_default_bold)

            pic_format = (
                embed_ast_conf.pic_format
                if embed_ast_conf.imagick
                else embed_ast_conf.pic_fallback
            )
            thumbnail = clean_filename(wp_slug, pic_format)
            logging.info(f"Thumbnail name: {thumbnail}")

            try:
                workflows.fetch_thumbnail(
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
                img_attrs = workflows.make_img_payload(
                    title, db_interface.get_description()
                )
                logging.info(f"Image Attrs: {img_attrs}")
                upload_img = wordpress_api.upload_thumbnail(
                    wpauths.api_base_url,
                    [wp_endpoints.media],
                    f"{os.path.join(thumbnails_dir.name, thumbnail)}",
                    img_attrs,
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
                elif upload_img == (200 or 201):
                    os.remove(
                        removed_img := f"{os.path.join(thumbnails_dir.name, thumbnail)}"
                    )
                    logging.info(f"Uploaded and removed: {removed_img}")

                console.print(
                    f"--> WordPress Media upload status code: {upload_img}",
                    style=user_default_bold,
                )
                console.print("--> Creating post on WordPress", style=user_default_bold)

                push_post = wordpress_api.wp_post_create([wp_endpoints.posts], payload)
                logging.info(f"WordPress post push status: {push_post}")
                console.print(
                    f"--> WordPress status code: {push_post}", style=user_default_bold
                )

                pyclip.detect_clipboard()
                pyclip.copy(db_interface.get_embed())
                pyclip.copy(title)
                console.print(
                    "--> Check the post and paste all you need from your clipboard.",
                    style=user_default_bold,
                )
                workflows.social_sharing_controller(
                    console, db_interface.get_description(), wp_slug, embed_ast_conf
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
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    workflows.terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                    logging.shutdown()
                    break
            if num < total_elems - 1:
                next_post = console.input(
                    f"[{user_prompt}]\nNext post? -> N/ENTER to review next post: [/{user_prompt}]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    logging.info("User declined further activity with the bot")
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    workflows.terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        videos_uploaded,
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
                cur_dump.close()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                workflows.terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        else:
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            workflows.terminate_loop_logging(
                console,
                num,
                total_elems,
                videos_uploaded,
                (h, mins, secs),
                exhausted=True,
            )


def main():
    try:
        if os.name == "posix":
            import readline

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
