"""
Config Model

This module defines the ConfigOption enum, which represents the possible configuration options in the
workflows_config.ini file.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypedDict


class ConfigOption(Enum):
    """Enum for configuration options in the workflows_config.ini file."""

    DEFAULT_STATUS = "default_status"
    ENABLE_LOGGING = "enable_logging"
    FALLBACK_PICTURE_FORMAT = "fallback_picture_format"
    FQDOMAIN_NAME = "fqdomain_name"
    IMAGE_QUALITY = "image_conversion_quality"
    IMAGE_SEO_ATTRIBUTES = "image_seo_attrs"
    IMAGICK_ENABLED = "imagick_enabled"
    LLM_MODEL_TAG = "llm_model_tag"
    LLM_PROVIDER = "llm_provider"
    LLM_PROVIDER_HOST = "llm_host"
    LLM_PROVIDER_PORT = "llm_port"
    PICTURE_FORMAT = "picture_format"
    TELEGRAM_SHARING = "telegram_sharing"
    TELEGRAM_SHARING_AUTO = "telegram_sharing_auto"
    WEBSITE_NAME = "website_name"
    X_POSTING_AUTO = "x_posting_auto"
    X_POSTING = "x_posting"
    SQL_QUERY = "sql_query"
    REVERSE_SLUG = "reverse_slug"
    DB_CONTENT_HINT = "db_content_hint"
    PARTNERS = "partners"
    ASSETS_CONF = "assets_conf"
    CAMPAIGN_ID = "campaign_id"
    CAMPAIGN_UTM = "campaign_utm"
    SOURCE_ID = "source_id"
    FEED_DUMP_URL = "feed_dump_url"
    FEED_SET_URL = "feed_set_url"
    ASSETS_ENABLED = "assets_enabled"
    SOCIAL_CONFIG_OVERRIDE = "social_config_override"


class ConfigSection(Enum):
    """Enum for configuration sections in the workflows_config.ini file."""

    GENERAL_CONFIG = "general_config"
    IMAGE_CONFIG = "image_configs"
    AI_CONFIG = "ai_configs"
    SOCIAL_POSTING = "social_posting"
    CONTENT_BOT = "content_bot"
    EMBED_ASSIST_BOT = "embed_assist_bot"
    GALLERY_BOT = "gallery_bot"
    FEED_ALPHA = "feed_alpha"
    FEED_BETA = "feed_beta"
    FEED_DELTA = "feed_delta"
    WEB_SOURCES = "web_sources"


class ConfigModelDict(TypedDict):
    # ---- General Config
    website_name: str
    domain_name: str
    enable_logging: bool
    default_status: str
    # ---- Social Config
    x_posting: bool
    x_posting_auto: bool
    telegram_sharing: bool
    telegram_sharing_auto: bool
    social_config_override: bool
    # ---- Image Config
    image_seo: bool
    picture_format: str
    enable_imagick: bool
    img_quality: int
    fallback_img_format: str
    # ---- AI Config
    llm_model_tag: str
    llm_providers: str
    llm_host: str
    llm_port: int
    # ---- FeedAlpha
    feed_alpha_campaign_id: int
    # ---- FeedBeta Feed
    feed_beta_source_id: int
    # ---- FeedDelta Feed
    feed_delta_campaign_utm: str
    # ---- MediaSource Content Bot
    media_source_sql_query: str
    media_source_x_posting: bool
    media_source_x_posting_auto: bool
    media_source_telegram_sharing: bool
    media_source_telegram_sharing_auto: bool
    media_source_partners: str
    media_source_assets_conf: str
    media_source_assets_enabled: bool
    # ---- MediaSource Gallery Bot
    media_source_gallery_sql_query: str
    media_source_gallery_x_posting: bool
    media_source_gallery_x_posting_auto: bool
    media_source_gallery_telegram_sharing: bool
    media_source_gallery_telegram_sharing_auto: bool
    media_source_gallery_partners: str
    # ---- Vid Embed Bot
    vid_embed_sql_query: str
    vid_embed_x_posting: bool
    vid_embed_x_posting_auto: bool
    vid_embed_telegram_sharing: bool
    vid_embed_telegram_sharing_auto: bool
    vid_embed_partners: str


@dataclass(frozen=True, kw_only=True)
class GeneralConfigs:
    """
    Immutable dataclass responsible for holding
    bot configuration variables and behavioural tweaks.
    """

    enable_logging: bool
    site_name: str
    fq_domain_name: str
    default_status: str

    def __repr__(self):
        return "GeneralConfigs()"


@dataclass(frozen=True, kw_only=True)
class SocialPostingConfig:
    """
    Immutable dataclass responsible for influencing
    bot social posting behaviour.
    """

    telegram_sharing_auto: bool
    telegram_sharing: bool
    x_posting_auto: bool
    x_posting: bool
    social_config_override: bool

    def __repr__(self):
        return "SocialPostingConfig()"


@dataclass(frozen=True, kw_only=True)
class ImageConfig:
    """
    Immutable dataclass responsible for holding
    bot configuration variables and behavioural tweaks.
    """

    img_conversion_quality: Optional[int]
    img_seo_attrs: Optional[bool]
    imagick: Optional[bool]
    pic_fallback: Optional[str]
    pic_format: Optional[str]

    def __repr__(self):
        return "ImageConfig()"


@dataclass(frozen=True, kw_only=True)
class AIServices:
    """
    Immutable data class for the configuration of large language model (LLM) providers.
    """

    llm_provider: str
    llm_model_tag: str
    llm_serve_host: str
    llm_serve_port: int

    def __repr__(self):
        return "AIServices()"


@dataclass(frozen=True, kw_only=True)
class ContentBotConf:
    """
    Immutable dataclass responsible for holding content-select
    bot configuration variables and behavioural tweaks.
    """

    assets_conf: str
    assets_enabled: bool
    content_hint: str
    partners: str
    sql_query: str
    telegram_sharing_auto: bool
    telegram_sharing_enabled: bool
    x_posting_auto: bool
    x_posting_enabled: bool

    def __repr__(self):
        return "ContentBotConf()"


@dataclass(frozen=True, kw_only=True)
class GalleryBotConf:
    """
    Immutable dataclass responsible for holding gallery-select
    bot configuration variables and behavioural tweaks.
    """

    content_hint: str
    partners: str
    sql_query: str
    telegram_sharing_auto: bool
    telegram_sharing_enabled: bool
    x_posting_auto: bool
    x_posting_enabled: bool

    def __repr__(self):
        return "GalleryBotConf()"


@dataclass(frozen=True, kw_only=True)
class EmbedAssistBotConf:
    """
    Immutable dataclass responsible for holding embed-assist
    bot configuration variables and behavioural tweaks.
    """

    content_hint: str
    partners: str
    sql_query: str
    telegram_sharing_auto: bool
    telegram_sharing_enabled: bool
    x_posting_auto: bool
    x_posting_enabled: bool

    def __repr__(self):
        return "EmbedAssistBotConf()"


@dataclass(frozen=True, kw_only=True)
class WebSourcesConf:
    """
    Immutable dataclass for configuration constants for the ``tasks`` package.
    """

    feed_dump_url: str
    feed_set_url: str

    def __repr__(self):
        return "TasksConf()"


@dataclass(frozen=True, kw_only=True)
class FeedAlphaConf:
    """
    Immutable dataclass for configuration constants for the ``FeedAlpha`` API.
    """

    campaign_id: int

    def __repr__(self):
        return "FeedAlphaConf()"


@dataclass(frozen=True, kw_only=True)
class FeedBetaConf:
    """
    Immutable dataclass for configuration constants for the ``FeedBeta`` API.
    """

    source_id: int

    def __repr__(self):
        return "FeedBetaConf()"


@dataclass(frozen=True, kw_only=True)
class FeedDeltaConf:
    """
    Immutable dataclass for configuration constants for the ``FeedDelta`` API.
    """

    campaign_utm: str

    def __repr__(self):
        return "FeedDeltaConf()"
