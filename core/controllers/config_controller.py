"""
Config Controller Module

The ``config_controller`` module provides functions for creating and saving
configuration files for the project.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
from typing import List, Any

# Third-party modules
import gradio as gr

# Local implementations
from core.models.config_model import ConfigModelDict
from core.config import create_workflows_config
from core.config.config_factories import (
    reload_config,
    general_config_factory,
    social_config_factory,
    image_config_factory,
    feed_alpha_conf_factory,
    feed_beta_conf_factory,
    feed_delta_conf_factory,
    vid_embed_bot_conf_factory,
    content_bot_conf_factory,
    gallery_bot_conf_factory,
    web_sources_conf_factory,
)


from core.utils.config_writer import (
    GeneralConfig,
    SocialConfig,
    ImageConfig,
    FeedAlphaConfig,
    FeedBetaConfig,
    FeedDeltaConfig,
    ContentBotConfig,
    GalleryBotConfig,
    EmbedAssistBotConfig,
    WebSourcesConfig,
)


def save_config(conf_values: ConfigModelDict) -> None:
    config_results = [
        GeneralConfig.write_website_name(conf_values["website_name"]),
        GeneralConfig.write_fqdomain_name(conf_values["domain_name"].lower()),
        GeneralConfig.write_enable_logging(conf_values["enable_logging"]),
        GeneralConfig.write_default_status(conf_values["default_status"]),
        SocialConfig.write_x_social_posting(conf_values["x_posting"]),
        SocialConfig.write_x_posting_auto(conf_values["x_posting_auto"]),
        SocialConfig.write_telegram_sharing(conf_values["telegram_sharing"]),
        SocialConfig.write_telegram_sharing_auto(conf_values["telegram_sharing_auto"]),
        SocialConfig.write_social_config_override(
            conf_values["social_config_override"]
        ),
        ImageConfig.write_image_seo_attributes(conf_values["image_seo"]),
        ImageConfig.write_picture_format(conf_values["picture_format"].lower()),
        ImageConfig.write_imagick_enabled(conf_values["enable_imagick"]),
        ImageConfig.write_image_quality(conf_values["img_quality"]),
        ImageConfig.write_fallback_picture_format(
            conf_values["fallback_img_format"].lower()
        ),
        FeedAlphaConfig.write_campaign_id(conf_values["feed_alpha_campaign_id"]),
        FeedBetaConfig.write_source_id(conf_values["feed_beta_source_id"]),
        FeedDeltaConfig.write_campaign_utm(conf_values["feed_delta_campaign_utm"]),
        ContentBotConfig.write_db_query(conf_values["media_source_sql_query"]),
        ContentBotConfig.write_assets_enabled(conf_values["media_source_assets_enabled"]),
        ContentBotConfig.write_x_social_posting(conf_values["media_source_x_posting"]),
        ContentBotConfig.write_x_posting_auto(conf_values["media_source_x_posting_auto"]),
        ContentBotConfig.write_telegram_sharing(
            conf_values["media_source_telegram_sharing"]
        ),
        ContentBotConfig.write_telegram_sharing_auto(
            conf_values["media_source_telegram_sharing_auto"]
        ),
        ContentBotConfig.write_partner_names(conf_values["media_source_partners"]),
        GalleryBotConfig.write_db_query(conf_values["media_source_gallery_sql_query"]),
        GalleryBotConfig.write_x_social_posting(
            conf_values["media_source_gallery_x_posting"]
        ),
        GalleryBotConfig.write_x_posting_auto(
            conf_values["media_source_gallery_x_posting_auto"]
        ),
        GalleryBotConfig.write_telegram_sharing(
            conf_values["media_source_gallery_telegram_sharing"]
        ),
        GalleryBotConfig.write_telegram_sharing_auto(
            conf_values["media_source_gallery_telegram_sharing_auto"]
        ),
        GalleryBotConfig.write_partner_names(
            conf_values["media_source_gallery_partners"]
        ),
        EmbedAssistBotConfig.write_db_query(conf_values["vid_embed_sql_query"]),
        EmbedAssistBotConfig.write_x_social_posting(conf_values["vid_embed_x_posting"]),
        EmbedAssistBotConfig.write_x_posting_auto(
            conf_values["vid_embed_x_posting_auto"]
        ),
        EmbedAssistBotConfig.write_telegram_sharing(
            conf_values["vid_embed_telegram_sharing"]
        ),
        EmbedAssistBotConfig.write_telegram_sharing_auto(
            conf_values["vid_embed_telegram_sharing_auto"]
        ),
        EmbedAssistBotConfig.write_partner_names(conf_values["vid_embed_partners"]),
        WebSourcesConfig.write_api_url(conf_values["pw_api_base_url"]),
    ]
    success = all(config_results)
    if success:
        gr.Success("Configuration saved successfully!")
        logging.info("Configuration saved successfully! -> %s", conf_values)
    else:
        gr.Error("Failed to save configuration. Refresh and Try again...")
        logging.error("Failed to save configuration. Check your configuration file.")


def collect_config_state(
    site_name: str,
    fq_domain_name: str,
    logging_enabled: bool,
    post_status: str,
    x_social_enabled: bool,
    x_social_posting_auto: bool,
    general_telegram_enabled: bool,
    general_telegram_sharing_auto: bool,
    social_config_override: bool,
    seo_enabled: bool,
    preferred_pic_format: str,
    imagick_enabled: bool,
    image_quality: int,
    fallback_pic_format: str,
    feed_alpha_campaign: int,
    feed_beta_source: int,
    feed_delta_utm: str,
    vid_embed_sql_query: str,
    vid_embed_x_posting: bool,
    vid_embed_x_posting_auto: bool,
    vid_embed_telegram_sharing: bool,
    vid_embed_telegram_sharing_auto: bool,
    vid_embed_partners: str,
    mc_sql_query: str,
    mc_x_posting: bool,
    mc_x_posting_auto: bool,
    mc_telegram_sharing: bool,
    mc_telegram_sharing_auto: bool,
    mc_partners: str,
    mc_assets_enabled: bool,
    mc_assets_conf: str,
    mc_gallery_sql_query: str,
    mc_gallery_x_posting: bool,
    mc_gallery_x_posting_auto: bool,
    mc_gallery_telegram_sharing: bool,
    mc_gallery_telegram_sharing_auto: bool,
    mc_gallery_partners: str,
    pw_api_url: str,
) -> None:
    config_states: ConfigModelDict = {
        "website_name": site_name,
        "domain_name": fq_domain_name,
        "enable_logging": logging_enabled,
        "default_status": post_status,
        "x_posting": x_social_enabled,
        "x_posting_auto": x_social_posting_auto,
        "telegram_sharing": general_telegram_enabled,
        "telegram_sharing_auto": general_telegram_sharing_auto,
        "social_config_override": social_config_override,
        "image_seo": seo_enabled,
        "picture_format": preferred_pic_format,
        "enable_imagick": imagick_enabled,
        "img_quality": image_quality,
        "fallback_img_format": fallback_pic_format,
        "feed_alpha_campaign_id": feed_alpha_campaign,
        "feed_delta_campaign_utm": feed_delta_utm,
        "feed_beta_source_id": feed_beta_source,
        "media_source_assets_enabled": mc_assets_enabled,
        "media_source_sql_query": mc_sql_query,
        "media_source_x_posting": mc_x_posting,
        "media_source_x_posting_auto": mc_x_posting_auto,
        "media_source_telegram_sharing": mc_telegram_sharing,
        "media_source_telegram_sharing_auto": mc_telegram_sharing_auto,
        "media_source_partners": mc_partners,
        "media_source_assets_conf": mc_assets_conf,
        "media_source_gallery_sql_query": mc_gallery_sql_query,
        "media_source_gallery_x_posting": mc_gallery_x_posting,
        "media_source_gallery_x_posting_auto": mc_gallery_x_posting_auto,
        "media_source_gallery_telegram_sharing": mc_gallery_telegram_sharing,
        "media_source_gallery_telegram_sharing_auto": mc_gallery_telegram_sharing_auto,
        "media_source_gallery_partners": mc_gallery_partners,
        "vid_embed_sql_query": vid_embed_sql_query,
        "vid_embed_x_posting": vid_embed_x_posting,
        "vid_embed_x_posting_auto": vid_embed_x_posting_auto,
        "vid_embed_telegram_sharing": vid_embed_telegram_sharing,
        "vid_embed_telegram_sharing_auto": vid_embed_telegram_sharing_auto,
        "vid_embed_partners": vid_embed_partners,
        "pw_api_base_url": pw_api_url,
    }
    save_config(config_states)
    return None


def load_config_fields() -> List[Any]:
    reload_config()
    config = ConfigModelDict(
        website_name=general_config_factory().site_name,
        domain_name=general_config_factory().fq_domain_name,
        enable_logging=general_config_factory().enable_logging,
        default_status=general_config_factory().default_status,
        x_posting=social_config_factory().x_posting,
        x_posting_auto=social_config_factory().x_posting_auto,
        telegram_sharing=social_config_factory().telegram_sharing,
        telegram_sharing_auto=social_config_factory().telegram_sharing_auto,
        social_config_override=social_config_factory().social_config_override,
        image_seo=image_config_factory().img_seo_attrs,
        picture_format=image_config_factory().pic_format,
        enable_imagick=image_config_factory().imagick,
        img_quality=image_config_factory().img_conversion_quality,
        fallback_img_format=image_config_factory().pic_fallback,
        feed_alpha_campaign_id=feed_alpha_conf_factory().campaign_id,
        feed_beta_source_id=feed_beta_conf_factory().source_id,
        feed_delta_campaign_utm=feed_delta_conf_factory().campaign_utm,
        vid_embed_sql_query=vid_embed_bot_conf_factory().sql_query,
        vid_embed_x_posting=vid_embed_bot_conf_factory().x_posting_enabled,
        vid_embed_x_posting_auto=vid_embed_bot_conf_factory().x_posting_auto,
        vid_embed_telegram_sharing=vid_embed_bot_conf_factory().telegram_sharing_enabled,
        vid_embed_telegram_sharing_auto=vid_embed_bot_conf_factory().telegram_sharing_auto,
        vid_embed_partners=vid_embed_bot_conf_factory().partners,
        media_source_sql_query=content_bot_conf_factory().sql_query,
        media_source_x_posting=content_bot_conf_factory().x_posting_enabled,
        media_source_x_posting_auto=content_bot_conf_factory().x_posting_auto,
        media_source_telegram_sharing=content_bot_conf_factory().telegram_sharing_enabled,
        media_source_telegram_sharing_auto=content_bot_conf_factory().telegram_sharing_auto,
        media_source_partners=content_bot_conf_factory().partners,
        media_source_assets_enabled=content_bot_conf_factory().assets_enabled,
        media_source_assets_conf=content_bot_conf_factory().assets_conf,
        media_source_gallery_sql_query=gallery_bot_conf_factory().sql_query,
        media_source_gallery_x_posting=gallery_bot_conf_factory().x_posting_enabled,
        media_source_gallery_x_posting_auto=gallery_bot_conf_factory().x_posting_auto,
        media_source_gallery_telegram_sharing=gallery_bot_conf_factory().telegram_sharing_enabled,
        media_source_gallery_telegram_sharing_auto=gallery_bot_conf_factory().telegram_sharing_auto,
        media_source_gallery_partners=gallery_bot_conf_factory().partners,
        pw_api_base_url=web_sources_conf_factory().pw_api_base_url,
    )
    return list(config.values())


def repair_from_template() -> None:
    """
    Create the workflows configuration file using the default template.
    """
    repair_result = create_workflows_config(repair_from_template=True)
    if repair_result:
        gr.Success("Configuration file repaired successfully!")
        gr.Info("Stop the application and restart it to apply the changes.")
        reload_config()
    else:
        gr.Error("Failed to repair configuration. Check your configuration file.")
    logging.info(f"User requested repair from template -> Result: {repair_result}")
    return None
