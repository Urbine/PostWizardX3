"""
WorkflowMediaPayload builder class

This class provides factory methods for ``MediaAttributePayload`` class of the ``WordPress`` package.
Factory methods here are used to create specialised payloads for the media attributes of WordPress posts
handled with workflows in this package.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Union, Tuple, Dict

from core.config.config_factories import general_config_factory, image_config_factory
from core.models.config_model import GeneralConfigs, ImageConfig
from wordpress.builders import MediaAttributePayload


class WorkflowMediaPayload(MediaAttributePayload):
    """
    WorkflowMediaPayload builder class

    Provide factory methods for creating specialised payloads for the media attributes of WordPress posts
    handled with workflows in this package.
    """

    def __init__(self):
        super().__init__()

    def payload_factory(
        self,
        vid_title: str,
        vid_description: str,
        flat_payload: Union[bool, Tuple[str, str, str]] = False,
    ) -> Dict[str, str]:
        """
        Factory method for class ``WorkflowMediaPayload`` to make WordPress ``JSON`` payload with the supplied values.

        Some elements are not passed as f-strings because the ``WordPress JSON REST API`` has defined a different data types
        for those elements and, sometimes, the response returns a status code of 400
        when those are not followed carefully.

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

        if vid_title == vid_description and not flat_payload:
            alt_text = f"{vid_title} on {general_config.site_name}"
            caption = f"{vid_title} on {general_config.fq_domain_name}"
            description = f"{vid_title} on {general_config.fq_domain_name}"
        elif not image_conf.img_seo_attrs:
            alt_text = ""
            caption = ""
            description = ""
        elif not flat_payload:
            alt_text = (
                f"{vid_title} on {general_config.fq_domain_name} - {vid_description}"
            )
            caption = (
                f"{vid_title} on {general_config.fq_domain_name} - {vid_description}"
            )
            description = (
                f"{vid_title} on {general_config.fq_domain_name} - {vid_description}"
            )
        else:
            alt_text = flat_payload[0]
            caption = flat_payload[1]
            description = flat_payload[2]

        return (
            self.alt_text(alt_text)
            .caption(caption)
            .description(description)
            .build(mutable=True)
        )

    def gallery_payload_factory(
        self,
        gal_title: str,
        iternum: int,
        gallery_sel_conf: ImageConfig = image_config_factory(),
    ) -> Dict[str, str]:
        """Make the image gallery payload that will be sent with the PUT/POST request
        to the WordPress media endpoint in every image gallery photo upload

        :param gal_title: ``str`` Gallery title/name
        :param iternum: ``int`` short for "iteration number" and it allows for image numbering in the payload.
        :param gallery_sel_conf: ``ImageConfig`` - Image configuration object
        :return: ``dict[str, str]``
        """
        img_attrs: bool = gallery_sel_conf.img_seo_attrs
        payload_content = f"Photo {iternum} from {gal_title}" if img_attrs else ""
        return (
            self.alt_text(payload_content)
            .caption(payload_content)
            .description(payload_content)
            .build(mutable=True)
        )
