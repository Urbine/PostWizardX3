"""
WorkflowPostPayload class

This class extends the ``WordPress`` payload builder and adds the models list to it.
This payload builder is specific to the workflows contained in this package.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self, List, Optional, Dict, Union

from core.config.config_factories import general_config_factory, image_config_factory
from core.models.config_model import GeneralConfigs, ImageConfig
from wordpress.builders import PostPayloadBuilder
from wordpress.models import PayloadItem


class WorkflowPostPayloadBuilder(PostPayloadBuilder):
    """
    WorkflowPostPayloadBuilder class

    This class extends the ``WordPress`` payload builder and adds the models list to it.
    """

    def __init__(self):
        super().__init__()

    def models(self, models: List[int]) -> Self:
        """
        Add a models list to the payload.

        :param models:  ``list[int]`` -> The numeric models to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.PORNSTARS, models)
        return self

    def payload_factory_mcash(
        self,
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
        """
        Factory method for class ``WorkflowPostPayloadBuilder`` to make WordPress ``JSON`` payload with the supplied values.
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
        content = (
            f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt="{vid_name} | {partner_name} on {general_conf.fq_domain_name}"/></a></figure>'
            if img_attrs
            else f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt=""/></a></figure>'
        )
        post_payload = (
            self.slug(f"{vid_slug}")
            .status(f"{status_wp}")
            .type("post")
            .title(f"{vid_name}")
            .excerpt(f"<p>{vid_description}</p>\n")
            .content(content)
            .featured_media(0)
            .tags(tag_int_lst)
            .models(model_int_lst)
        )

        if categs:
            post_payload.categories(categs)

        return post_payload.build(mutable=True)

    def payload_factory_simple(
        self,
        vid_slug,
        status_wp: str,
        vid_name: str,
        vid_description: str,
        tag_int_lst: List[int],
        model_int_lst: Optional[List[int]] = None,
        categs: Optional[List[int]] = None,
    ) -> Optional[Dict[str, Union[str, int]]]:
        """
        Factory method for class ``WorkflowPostPayloadBuilder`` to make WordPress ``JSON`` payload with the supplied values.

        :param vid_slug: ``str`` slug optimized by the job control function and database parsing algorithm ( ``tasks`` package).
        :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
        :param vid_name: ``str`` self-explanatory
        :param vid_description: ``str`` self-explanatory
        :param tag_int_lst: ``list[int]`` tag ID list
        :param model_int_lst: ``list[int]`` or ``None`` model ID list
        :param categs: ``list[int]`` or ``None`` category integers provided as optional parameter.
        :return: ``dict[str, str | int]``
        """
        post_payload = (
            self.slug(f"{vid_slug}")
            .status(f"{status_wp}")
            .type("post")
            .title(f"{vid_name}")
            .excerpt(f"<p>{vid_description}</p>\n")
            .content(f"<p>{vid_description}")
            .featured_media(0)
            .tags(tag_int_lst)
        )

        if categs:
            post_payload.categories(categs)

        if model_int_lst:
            post_payload.models(model_int_lst)

        return post_payload.build(mutable=True)
