"""
Workflow Builders module

This module is responsible for building the payloads for the WordPress posts and images.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import re
import shutil
from typing import List, Optional, Dict, Union, Tuple

# Local imports
from core.config.config_factories import general_config_factory, image_config_factory
from core.models.config_model import GeneralConfigs, ImageConfig
from core.utils.file_system import search_files_by_ext
from core.utils.strings import split_char
from wordpress import WordPress
from workflows.utils.strings import clean_partner_tag


def make_payload(
    vid_slug,
    status_wp: str,
    vid_name: str,
    vid_description: str,
    banner_tracking_url: str,
    banner_img: str,
    partner_name: str,
    tag_int_lst: List[int],
    model_int_lst: List[int],
    categs: Optional[List[int]] = None,
) -> Dict[str, Union[str, int]]:
    """Make WordPress ``JSON`` payload with the supplied values.
    This function also injects ``HTML`` code into the payload to display the banner, add ``ALT`` text to it
    and other parameters for the WordPress editor's (Gutenberg) rendering.

    Some elements are not passed as f-strings because the ``WordPress JSON REST API`` has defined a different data types
    for those elements and, sometimes, the response returns a status code of 400
    when those are not followed carefully.

    :param vid_slug: ``str`` slug optimized by the job control function and database parsing algo ( ``tasks`` package).
    :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
    :param vid_name: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param banner_tracking_url: ``str`` Affiliate tracking link to generate leads
    :param banner_img: ``str`` banner image URL that will be injected into the payload.
    :param partner_name: ``str`` The offer you are promoting
    :param tag_int_lst: ``list[int]`` tag ID list
    :param model_int_lst: ``list[int]`` model ID list
    :param categs: ``list[int]`` category numbers to be passed with the post information
    :return: ``dict[str, str | int]``
    """
    general_conf: GeneralConfigs = general_config_factory()
    image_conf: ImageConfig = image_config_factory()
    img_attrs: bool = image_conf.img_seo_attrs
    payload_post: Dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "title": f"{vid_name}",
        "excerpt": f"<p>{vid_description}</p>\n",
        "content": f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt="{vid_name} | {partner_name} on {general_conf.fq_domain_name}"/></a></figure>'
        if img_attrs
        else f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt=""/></a></figure>',
        "featured_media": 0,
        "tags": tag_int_lst,
        "pornstars": model_int_lst,
    }

    if categs:
        payload_post["categories"] = categs

    return payload_post


def make_payload_simple(
    vid_slug,
    status_wp: str,
    vid_name: str,
    vid_description: str,
    tag_int_lst: List[int],
    model_int_lst: Optional[List[int]] = None,
    categs: Optional[List[int]] = None,
) -> Dict[str, Union[str, int]]:
    """Makes a simple WordPress JSON payload with the supplied values.

    :param vid_slug: ``str`` slug optimized by the job control function and database parsing algo ( ``tasks`` package).
    :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
    :param vid_name: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param tag_int_lst: ``list[int]`` tag ID list
    :param model_int_lst: ``list[int]`` or ``None`` model ID list
    :param categs: ``list[int]`` or ``None`` category integers provided as optional parameter.
    :return: ``dict[str, str | int]``
    """
    payload_post: Dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "title": f"{vid_name}",
        "content": f"<p>{vid_description}",
        "excerpt": f"<p>{vid_description}</p>\n",
        "featured_media": 0,
        "tags": tag_int_lst,
    }

    if categs:
        payload_post["categories"] = categs
    elif model_int_lst:
        payload_post["pornstars"] = model_int_lst

    return payload_post


def make_img_payload(
    vid_title: str,
    vid_description: str,
    flat_payload: Union[bool, Tuple[str, str, str]] = False,
) -> Dict[str, str]:
    """Similar to the make_payload function, this one makes the payload for the video thumbnails,
    it gives them the video description and focus key phrase, which is the video title plus a call to
    action in case that a certain ALT text appears on the image search vertical, and they want to watch the video.

    :param vid_title: ``str`` The title of the video.
    :param vid_description: ``str`` The description of the video.
    :param flat_payload: ``bool | tuple[str, str, str]``, optional
        When ``False`` (default), the payload is generated automatically.
        If a tuple of (`alt_text`, `caption`, `description`) is provided, it is used to create the payload.
    :return: ``Dict[str, str]`` A dictionary with the image payload.
    """
    general_config: GeneralConfigs = general_config_factory()
    image_conf: ImageConfig = image_config_factory()

    # In case that the description is the same as the title, the program will send
    # a different payload to avoid keyword over-optimization.
    flat_attrs_dict = {
        "alt_text": "",
        "caption": "",
        "description": "",
    }

    if vid_title == vid_description and not flat_payload:
        img_payload: Dict[str, str] = {
            "alt_text": f"{vid_title} on {general_config.site_name}",
            "caption": f"{vid_title} on {general_config.fq_domain_name}",
            "description": f"{vid_title} {general_config.fq_domain_name}",
        }
    elif not image_conf.img_seo_attrs:
        img_payload = flat_attrs_dict
    elif not flat_payload:
        img_payload: Dict[str, str] = {
            "alt_text": f"{vid_title} on {general_config.fq_domain_name} - {vid_description}",
            "caption": f"{vid_title} on {general_config.fq_domain_name} - {vid_description}",
            "description": f"{vid_title} on {general_config.fq_domain_name} - {vid_description}",
        }
    else:
        flat_attrs_dict["alt_text"] = flat_payload[0]
        flat_attrs_dict["caption"] = flat_payload[1]
        flat_attrs_dict["description"] = flat_payload[2]
        img_payload = flat_attrs_dict

    return img_payload


def make_slug(
    partner: str,
    model: Optional[str],
    title: str,
    content: str,
    studio: Optional[str] = "",
    reverse: bool = False,
    partner_out: bool = False,
) -> str:
    """This function is a new approach to the generation of slugs inspired by the slug-making
    mechanism from gallery_select.py. It takes in strings that will be transformed into URL slugs
    that will help us optimise the permalinks for SEO purposes.

    :param partner: ``str`` video partner
    :param model:  ``str`` video model
    :param title: ``str`` Video title
    :param content: ``str`` type of content, in this file it is simply `video` but it could be `pics` this parameter tells Google about the main content of the page.
    :param studio: ``str`` - Optional component in slugs for compatible schemas.
    :param reverse: ``bool``  ``True`` if you want to place the video title in front of the permalink. Default ``False``
    :param partner_out: ``bool`` ``True`` if you want to build slugs without the partner name. Default ``False``.
    :return: ``str`` formatted string of a WordPress-ready URL slug.
    """
    join_wrds = lambda wrd: "-".join(map(lambda w: w.lower(), re.findall(r"\w+", wrd)))  # noqa: E731
    build_slug = lambda lst: "-".join(filter(lambda e_str: e_str != "", lst))  # noqa: E731

    # Punctuation marks are filtered in ``title_cleaned``.
    # TODO: Add a list of corpus stopwords from the NLTK library.
    filter_words: List[str] = [
        "at",
        "&",
        "and",
        "but",
        "it",
        "so",
        "very",
        "amp;",
        "",
        "&amp",
    ]

    title_cleaned: List[str] = [
        "".join(wrd).lower()
        for word in title.lower().split()
        if (wrd := re.findall(r"\w+", word, flags=re.IGNORECASE))
    ]

    title_sl: str = "-".join(
        list(filter(lambda w: w not in filter_words, title_cleaned))
    )

    partner_sl: str = "-".join(clean_partner_tag(partner.lower()).split())
    content_sl: str = join_wrds(content)
    studio_sl: str = join_wrds(studio) if studio is not None else ""

    model_sl: str = ""
    if model:
        model_delim = split_char(model, placeholder=" ")
        model_sl = "-".join(
            "-".join(map(join_wrds, name.split(" ")))
            for name in map(
                lambda m: m.lower().strip(),
                model.split(model_delim if model_delim != " " else "."),
            )
        )

    # Build slug segments according to flags
    segments: List[str]
    if reverse:
        # reverse has precedence over every other flag
        segments = [title_sl, partner_sl]
        if model_sl:
            segments.append(model_sl)
        if studio_sl:
            segments.append(studio_sl)
        segments.append(content_sl)
    elif partner_out:
        # partner name omitted
        segments = [title_sl]
        if model_sl:
            segments.append(model_sl)
        elif studio_sl:
            segments.append(studio_sl)
        segments.append(content_sl)
    else:
        # default behaviour
        segments = [partner_sl]
        if model_sl:
            segments.append(model_sl)
        segments.append(title_sl)
        if studio_sl:
            segments.append(studio_sl)
        segments.append(content_sl)

    return build_slug(segments)


def make_gallery_payload(
    gal_title: str,
    iternum: int,
    gallery_sel_conf: ImageConfig = image_config_factory(),
):
    """Make the image gallery payload that will be sent with the PUT/POST request
    to the WordPress media endpoint.

    :param gal_title: ``str`` Gallery title/name
    :param iternum: ``str`` short for "iteration number" and it allows for image numbering in the payload.
    :param gallery_sel_conf: ``GallerySelectConf`` - Bot configuration object
    :return: ``dict[str, str]``
    """
    img_attrs: bool = gallery_sel_conf.img_seo_attrs
    img_payload: Dict[str, str] = {
        "alt_text": f"Photo {iternum} from {gal_title}" if img_attrs else "",
        "caption": f"Photo {iternum} from {gal_title}" if img_attrs else "",
        "description": f"Photo {iternum} from {gal_title}" if img_attrs else "",
    }
    return img_payload


def make_photos_post_payload(
    status_wp: str,
    set_name: str,
    partner_name: str,
    tags: List[int],
    reverse_slug: bool = False,
) -> Dict[str, Union[str, int]]:
    """Construct the photos payload that will be sent with all the parameters for the
    WordPress REST API request to create a ``photos`` post.
    In addition, this function makes the permalink that I will be using for the post.

    :param status_wp: ``str`` typically ``draft`` but it can be ``publish``, however, all posts need review.
    :param set_name: ``str`` photo gallery name.
    :param partner_name: ``str`` partner offer that I am promoting
    :param tags: ``list[int]`` tag IDs that will be sent to WordPress for classification and integration.
    :param reverse_slug: ``bool`` ``True`` if you want to reverse the permalink (slug) construction.
    :return: ``dict[str, str | int]``
    """
    # TODO: Use corpus stopwords from the NLTK library.
    filter_words: set[str] = {"on", "in", "at", "&", "and"}

    no_partner_name: List[str] = list(
        filter(lambda w: w not in set(partner_name.split(" ")), set_name.split(" "))
    )

    # no_partner_name: list[str] = [
    #     word for word in set_name.split(" ") if word not in set(partner_name.split(" "))
    # ]

    wp_pre_slug: str = "-".join(
        [
            word.lower()
            for word in no_partner_name
            if re.match(r"\w+", word, flags=re.IGNORECASE)
            and word.lower() not in filter_words
        ]
    )

    if reverse_slug:
        # '-pics' tells Google the main content of the page.
        final_slug: str = (
            f"{wp_pre_slug}-{'-'.join(partner_name.lower().split(' '))}-pics"
        )
    else:
        final_slug: str = (
            f"{'-'.join(partner_name.lower().split(' '))}-{wp_pre_slug}-pics"
        )
    # Setting Env variable since the slug is needed outside this function.
    os.environ["SET_SLUG"] = final_slug

    payload_post: Dict[str, Union[str, int]] = {
        "slug": final_slug,
        "status": f"{status_wp}",
        "type": "photos",
        "title": f"{set_name}",
        "featured_media": 0,
        "photos_tag": tags,
    }
    return payload_post


def upload_image_set(
    ext: str,
    folder: str,
    title: str,
    wordpress_site: WordPress,
) -> None:
    """Upload a set of images to the WordPress Media endpoint.

    :param ext: ``str`` image file extension to look for.
    :param folder:  ``str`` Your thumbnails folder, just the name is necessary.
    :param title: ``str`` gallery name
    :param wordpress_site: ``WordPress`` instance
    :return: ``None``
    """
    thumbnails: List[str] = search_files_by_ext(ext, folder=folder)
    if len(thumbnails) == 0:
        # Assumes the thumbnails are contained in a directory
        # This could be caused by the archive extraction
        logging.info("Thumbnails contained in directory - Running recursive search")
        files: List[str] = search_files_by_ext(".jpg", recursive=True, folder=folder)

        get_parent_dir = lambda dr: os.path.split(os.path.split(dr)[-2:][0])[1]  # noqa: E731

        thumbnails: List[str] = [
            os.path.join(get_parent_dir(path), os.path.basename(path)) for path in files
        ]

    if len(thumbnails) != 0:
        logging.info(
            prnt_imgs
            := f"--> Uploading set with {len(thumbnails)} images to WordPress Media..."
        )
        print(prnt_imgs)
        print("--> Adding image attributes on WordPress...")
        thumbnails.sort()

    # Prepare the image new name so that separators are replaced by hyphens.
    # E.g. this_is_a_cool_pic.jpg => this-is-a-cool-pic.jpg
    new_name_img = lambda name: "-".join(  # noqa: E731
        f"{os.path.basename(name)!s}".split(split_char(name))
    )

    for number, image in enumerate(thumbnails, start=1):
        img_attrs: Dict[str, str] = make_gallery_payload(title, number)
        img_file = "-".join(
            new_name_img(image).split(split_char(image, placeholder=" "))
        )
        os.renames(
            os.path.join(folder, os.path.basename(image)),
            img_new := os.path.join(folder, os.path.basename(img_file)),
        )

        status_code: int = wordpress_site.upload_image(img_new, img_attrs)

        img_now = os.path.basename(img_new)
        if status_code == (200 or 201):
            logging.info(f"Removing --> {img_now}")
            os.remove(img_new)

        logging.info(
            img_seq := f"* Image {number} | {img_now} --> Status code: {status_code}"
        )
        print(img_seq)
    try:
        # Check if I have paths instead of filenames
        if len(thumbnails[0].split(os.sep)) > 1:
            try:
                shutil.rmtree(
                    remove_dir
                    := f"{os.path.join(os.path.abspath(folder), thumbnails[0].split(os.sep)[0])}"
                )
                logging.info(f"Removed dir -> {remove_dir}")
            except NotImplementedError:
                logging.info(
                    "Incompatible platform - Directory cleaning relies on tempdir logic for now"
                )
    except (IndexError, AttributeError):
        pass
