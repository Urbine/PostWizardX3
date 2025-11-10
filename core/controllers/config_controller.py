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
    adult_next_conf_factory,
    tube_corp_feed_conf_factory,
    fhouse_feed_conf_factory,
    vid_embed_bot_conf_factory,
    mcash_content_bot_conf_factory,
    mcash_gallery_bot_conf_factory,
    web_sources_conf_factory,
)


from core.utils.config_writer import (
    GeneralConfig,
    SocialConfig,
    ImageConfig,
    AdultNextFeedConfig,
    TubeCorpFeedConfig,
    FHouseFeedConfig,
    MCashContentBotConfig,
    MCashGalleryBotConfig,
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
        AdultNextFeedConfig.write_campaign_id(conf_values["anxt_campaign_id"]),
        TubeCorpFeedConfig.write_source_id(conf_values["tubecorp_source_id"]),
        FHouseFeedConfig.write_campaign_utm(conf_values["fp_house_campaign_utm"]),
        MCashContentBotConfig.write_db_query(conf_values["mcash_sql_query"]),
        MCashContentBotConfig.write_assets_enabled(conf_values["mcash_assets_enabled"]),
        MCashContentBotConfig.write_x_social_posting(conf_values["mcash_x_posting"]),
        MCashContentBotConfig.write_x_posting_auto(conf_values["mcash_x_posting_auto"]),
        MCashContentBotConfig.write_telegram_sharing(
            conf_values["mcash_telegram_sharing"]
        ),
        MCashContentBotConfig.write_telegram_sharing_auto(
            conf_values["mcash_telegram_sharing_auto"]
        ),
        MCashContentBotConfig.write_partner_names(conf_values["mcash_partners"]),
        MCashGalleryBotConfig.write_db_query(conf_values["mcash_gallery_sql_query"]),
        MCashGalleryBotConfig.write_x_social_posting(
            conf_values["mcash_gallery_x_posting"]
        ),
        MCashGalleryBotConfig.write_x_posting_auto(
            conf_values["mcash_gallery_x_posting_auto"]
        ),
        MCashGalleryBotConfig.write_telegram_sharing(
            conf_values["mcash_gallery_telegram_sharing"]
        ),
        MCashGalleryBotConfig.write_telegram_sharing_auto(
            conf_values["mcash_gallery_telegram_sharing_auto"]
        ),
        MCashGalleryBotConfig.write_partner_names(
            conf_values["mcash_gallery_partners"]
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
    anxt_campaign: int,
    tubecorp_source: int,
    fp_house_utm: str,
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
        "anxt_campaign_id": anxt_campaign,
        "fp_house_campaign_utm": fp_house_utm,
        "tubecorp_source_id": tubecorp_source,
        "mcash_assets_enabled": mc_assets_enabled,
        "mcash_sql_query": mc_sql_query,
        "mcash_x_posting": mc_x_posting,
        "mcash_x_posting_auto": mc_x_posting_auto,
        "mcash_telegram_sharing": mc_telegram_sharing,
        "mcash_telegram_sharing_auto": mc_telegram_sharing_auto,
        "mcash_partners": mc_partners,
        "mcash_assets_conf": mc_assets_conf,
        "mcash_gallery_sql_query": mc_gallery_sql_query,
        "mcash_gallery_x_posting": mc_gallery_x_posting,
        "mcash_gallery_x_posting_auto": mc_gallery_x_posting_auto,
        "mcash_gallery_telegram_sharing": mc_gallery_telegram_sharing,
        "mcash_gallery_telegram_sharing_auto": mc_gallery_telegram_sharing_auto,
        "mcash_gallery_partners": mc_gallery_partners,
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
        anxt_campaign_id=adult_next_conf_factory().campaign_id,
        tubecorp_source_id=tube_corp_feed_conf_factory().source_id,
        fp_house_campaign_utm=fhouse_feed_conf_factory().campaign_utm,
        vid_embed_sql_query=vid_embed_bot_conf_factory().sql_query,
        vid_embed_x_posting=vid_embed_bot_conf_factory().x_posting_enabled,
        vid_embed_x_posting_auto=vid_embed_bot_conf_factory().x_posting_auto,
        vid_embed_telegram_sharing=vid_embed_bot_conf_factory().telegram_sharing_enabled,
        vid_embed_telegram_sharing_auto=vid_embed_bot_conf_factory().telegram_sharing_auto,
        vid_embed_partners=vid_embed_bot_conf_factory().partners,
        mcash_sql_query=mcash_content_bot_conf_factory().sql_query,
        mcash_x_posting=mcash_content_bot_conf_factory().x_posting_enabled,
        mcash_x_posting_auto=mcash_content_bot_conf_factory().x_posting_auto,
        mcash_telegram_sharing=mcash_content_bot_conf_factory().telegram_sharing_enabled,
        mcash_telegram_sharing_auto=mcash_content_bot_conf_factory().telegram_sharing_auto,
        mcash_partners=mcash_content_bot_conf_factory().partners,
        mcash_assets_enabled=mcash_content_bot_conf_factory().assets_enabled,
        mcash_assets_conf=mcash_content_bot_conf_factory().assets_conf,
        mcash_gallery_sql_query=mcash_gallery_bot_conf_factory().sql_query,
        mcash_gallery_x_posting=mcash_gallery_bot_conf_factory().x_posting_enabled,
        mcash_gallery_x_posting_auto=mcash_gallery_bot_conf_factory().x_posting_auto,
        mcash_gallery_telegram_sharing=mcash_gallery_bot_conf_factory().telegram_sharing_enabled,
        mcash_gallery_telegram_sharing_auto=mcash_gallery_bot_conf_factory().telegram_sharing_auto,
        mcash_gallery_partners=mcash_gallery_bot_conf_factory().partners,
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
