"""
WordPress Reporting module

This module provides functions to aggregate and report on WordPress site data,
including posts, tags, categories, and dedicated taxonomies.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import datetime
import os
import sqlite3

from argparse import ArgumentParser
from typing import Generator

# Third-party imports
import xlsxwriter

# Local imports
from core.utils.file_system import is_parent_dir_required, remove_if_exists
from core.utils.strings import clean_filename
from core.controllers.secrets_controller import SecretHandler
from core.models.secret_model import SecretType, WPSecrets
from core.models.file_system import ApplicationPath, ProjectFile
from core.exceptions.util_exceptions import NoSuitableArgument

from wordpress_api import WordPress
from wordpress.models.taxonomies import WPTaxonomyMarker, WPTaxonomyValues

from core.config.config_factories import general_config_factory


def unpack_tpl_excel(tupled_list: tuple[tuple[str]]) -> Generator[str, None, None]:
    """This function was created to write the ``Tuple`` (by coercion) contents of
    another function into an ``.xlsx`` file cell appropriately.
    It was created to address an unwanted behaviour in this line specifically:
    ``tuple(map_tags_posts(wp_posts_f, idd='y').values())`` in the ``create_tag_report_excel`` function.

    :param tupled_list: list of tuples
    :return: ``Generator[str, None, None]`` *Generator with a ``YieldType`` of ``str``*
    """
    for item in tupled_list:
        yield "".join(str(item)).strip("[']")


def create_tag_report_excel(
    wordpress_site: WordPress, workbook_name: str, parent: bool = False
) -> None:
    """Write the tagging information into an Excel ``.xlsx`` file.

    :param parent: ``bool`` Place the workbook in the parent directory if ``True``, default ``False``.
    :param wordpress_site: ``WordPress`` instance responsible for managing all the
                             WordPress site data.
    :param workbook_name: ``str`` workbook name with or without extension.
    :return: ``None``
    """
    try:
        from core.config.config_factories import mcash_content_bot_conf_factory

        hints = mcash_content_bot_conf_factory().partners.split(",")
    except ModuleNotFoundError:
        hints = []

    workbook_fname = clean_filename(workbook_name, ".xlsx")
    dir_prefix = is_parent_dir_required(parent)

    tags_match_key = (WPTaxonomyMarker.TAG, WPTaxonomyValues.TAGS)
    tags_dict = wordpress_site.map_wp_class_id(tags_match_key[0], tags_match_key[1])
    tags_count = wordpress_site.count_wp_class_id(tags_match_key[0])

    model_wp_class_count = wordpress_site.count_map_match_taxonomy(
        WPTaxonomyMarker.MODELS, WPTaxonomyMarker.TAG, hints
    )

    workbook = xlsxwriter.Workbook(f"{dir_prefix}{workbook_fname}")

    tag_plus_tid = workbook.add_worksheet(name="Tag Fields & Videos Tagged")

    tag_plus_tid.set_column("A:C", 20)
    tag_plus_tid.set_column("D:E", 90)
    tag_plus_tid.write_row("A1", ("Tag", "Tag ID", "Videos Tagged", "Tagged IDs"))
    tag_plus_tid.write_column("A2", tuple(tags_dict.keys()))
    tag_plus_tid.write_column("B2", tuple(tags_dict.values()))
    tag_plus_tid.write_column("C2", tuple(tags_count.values()))
    tag_plus_tid.write_column(
        "D2",
        unpack_tpl_excel(
            wordpress_site.map_tags_posts(WPTaxonomyMarker.TAG, idd=True).values()
        ),
    )

    post_id_slug = workbook.add_worksheet(name="Post id & Post Slug")
    post_id_slug.set_column("A:A", 20)
    post_id_slug.set_column("B:B", 80)
    post_id_slug.set_column("C:C", 40)
    post_id_slug.write_row("A1", ("Post ID", "Post Slug", "Post Category"))
    post_id_slug.write_column("A2", tuple(wordpress_site.map_posts_by_id().keys()))
    post_id_slug.write_column(
        "B2",
        tuple(wordpress_site.map_posts_by_id(include_host_name=True).values()),
    )
    post_id_slug.write_column(
        "C2",
        unpack_tpl_excel(wordpress_site.map_postsid_category(host_name=True).values()),
    )

    model_count = workbook.add_worksheet(name="Video count by Model")
    model_count.set_column("A:A", 20)
    model_count.set_column("B:B", 15)
    model_count.set_column("C:C", 25)
    model_count.set_column("D:D", 50)
    model_count.write_row(
        "A1", ("Model Name", "Video Count", "Partner Name", "Post IDs")
    )
    model_count.write_column("A2", tuple(model_wp_class_count.keys()))
    model_count.write_column(
        "B2", (count[0][0] for count in model_wp_class_count.values())
    )
    model_count.write_column(
        "C2", (partner[0][1] for partner in model_wp_class_count.values())
    )
    par_strip = lambda tp: str(tp).strip(")").strip("(")
    t_comma_out = lambda tp: par_strip(tp) if len(tp) > 1 else par_strip(tp).strip(",")
    model_count.write_column(
        "D2",
        tuple(map(t_comma_out, map(lambda tp: tp[1:], model_wp_class_count.values()))),
    )

    workbook.close()

    print(
        f"\nFind the new file {workbook_fname} in \n{is_parent_dir_required(parent=parent)}\n"
    )
    return None


def update_published_titles_db(
    wordpress_site: WordPress,
    parent: bool = False,
    photosets: bool = False,
    yoast: bool = False,
) -> None:
    """Creates a ``SQLite`` db based on the WordPress site cached data that will be used by other modules to
        compare information in a different format. Sometimes, titles and descriptions can't be matched by
        the built-in ``re`` module in Python due to character sets or encodings present in different pieces of
        information extracted from WordPress. This is where, by having a db, we can conduct simple comparison
        operations without explicit pattern matching with ``re``.

    :param wordpress_site: ``WordPress`` object with file configuration information.
    :param parent: ``True`` if you want to place your database in the parent directory. Default ``False``.
    :param photosets: ``True`` if you want to build a photoset db. Default ``False``
    :param yoast: ``True`` if you have *Yoast SEO* plugin and want to increase accuracy, which is useful
                   when fields have unwanted HTML entities. Default ``False``.
    :return: ``None`` (Database file in working or parent directory)
    """
    db_name = (
        f"wp-photos-{datetime.date.today()}.db"
        if photosets
        else f"wp-posts-{datetime.date.today()}.db"
    )
    db_full_name = os.path.join(is_parent_dir_required(parent), db_name)
    remove_if_exists(db_full_name)
    db = sqlite3.connect(db_full_name)
    cur = db.cursor()
    if photosets:
        cur.execute("CREATE TABLE sets(title, model, wp_slug)")
        vid_slugs = wordpress_site.get_slugs()
        vid_titles = wordpress_site.get_post_titles_local(yoast_support=yoast)
        for title, slug in zip(vid_titles, vid_slugs):
            model = title.split(" ")[0]
            cur.execute(
                "INSERT INTO sets VALUES (?, ?, ?)", (title.title(), model, slug)
            )
        db.commit()
    else:
        cur.execute("CREATE TABLE videos(title, models, wp_slug)")
        vid_slugs = wordpress_site.get_slugs()
        vid_titles = wordpress_site.get_post_titles_local()
        vid_models = wordpress_site.get_post_models()
        for title, models, slug in zip(vid_titles, vid_models, vid_slugs):
            cur.execute("INSERT INTO videos VALUES (?, ?, ?)", (title, models, slug))
    db.commit()
    cur.close()
    db.close()


def get_site() -> WordPress:
    general_config = general_config_factory()
    wp_auth: WPSecrets = SecretHandler().get_secret(SecretType.WP_APP_PASSWORD)[0]
    wordpress_site = WordPress(
        general_config.fq_domain_name,
        wp_auth.user,
        wp_auth.app_password,
        ApplicationPath.WP_POSTS_CACHE.value,
    )
    return wordpress_site


def parse_args() -> ArgumentParser:
    args_parser = argparse.ArgumentParser(description="WordPress API Local Module")

    args_parser.add_argument(
        "--parent",
        action="store_true",
        default=False,
        help="Place the output of these functions in the relative parent directory.",
    )
    args_parser.add_argument(
        "--photos",
        action="store_true",
        default=False,
        help="Update the wp_photos local cache or associated files (db/config).",
    )
    args_parser.add_argument(
        "--posts",
        action="store_true",
        default=False,
        help="Update the wp_posts local cache or associated files (db/config).",
    )
    args_parser.add_argument(
        "--yoast",
        action="store_true",
        default=False,
        help="Enable Yoast SEO mode in compatible functions.",
    )
    args_parser.add_argument(
        "--excel",
        action="store_true",
        default=False,
        help="Create an MS Excel report with the tag and slug information of the site.",
    )
    return args_parser


def main():
    args = parse_args().parse_args()
    if args.excel:
        create_tag_report_excel(
            get_site(), ProjectFile.EXCEL_REPORT.value, parent=args.parent
        )
    elif args.photos:
        update_published_titles_db(
            get_site(), parent=args.parent, photosets=True, yoast=args.yoast
        )
    elif args.posts:
        update_published_titles_db(
            get_site(), parent=args.parent, photosets=False, yoast=args.yoast
        )
    else:
        raise NoSuitableArgument(__package__, __file__)


if __name__ == "__main__":
    main()
