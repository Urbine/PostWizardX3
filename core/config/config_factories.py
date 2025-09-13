"""
Configuration Factories Module

A module implementing the Factory pattern for creating configuration objects.
This module provides factory functions that construct immutable configuration
objects from INI configuration files.

Core responsibilities:
1. Utility functions for reloading configuration options
2. Factory functions for creating typed configuration objects
3. Centralized configuration loading and validation
4. Type-safe access to configuration parameters

Utility functions:
- reload_config(): Reloads the configuration file during runtime

Factory functions:
- general_config_factory(): Creates GeneralConfigs for basic app settings
- social_config_factory(): Creates SocialPostingConfig for social media features
- image_config_factory(): Creates ImageConfig for image processing settings
- ai_config_factory(): Creates AIServices for LLM integration settings

The factory pattern ensures:
- Configuration objects are created with validated data
- Type safety through dataclass implementations
- Single responsibility for configuration object creation
- Separation of configuration loading and usage

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


# Local implementations
from core.utils.parsers import parse_client_config
from core.exceptions.config_exceptions import ConfigFileNotFound, InvalidConfiguration
from core.config import create_workflows_config
from core.models.file_system import ApplicationPath, ProjectFile
from core.models.config_model import (
    AIServices,
    ConfigSection,
    ConfigOption,
    GeneralConfigs,
    ImageConfig,
    SocialPostingConfig,
    ContentBotConf,
    GalleryBotConf,
    EmbedAssistBotConf,
    FeedAlphaConf,
    FeedBetaConf,
    FeedDeltaConf,
    WebSourcesConf,
)

try:
    WORKFLOWS_CONFIG_INI = parse_client_config(
        ProjectFile.WORKFLOWS_CONFIG.value, ApplicationPath.CONFIG_PKG.value
    )
except ConfigFileNotFound:
    # If the file doesn't exist, create it
    create_workflows_config()


# --- Utilities ---
def reload_config() -> None:
    """Reload the configuration file and clear the garbage collector."""
    global WORKFLOWS_CONFIG_INI
    WORKFLOWS_CONFIG_INI = parse_client_config(
        ProjectFile.WORKFLOWS_CONFIG.value, ApplicationPath.CONFIG_PKG.value
    )
    return None


# --- Factories ---
def general_config_factory() -> GeneralConfigs:
    """Factory function for dataclass ``GeneralConfigs``

    :return: ``GeneralConfigs``
    """
    section = ConfigSection.GENERAL_CONFIG.value
    try:
        return GeneralConfigs(
            site_name=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.WEBSITE_NAME.value
            ),
            enable_logging=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.ENABLE_LOGGING.value
            ),
            fq_domain_name=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.FQDOMAIN_NAME.value
            ),
            default_status=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.DEFAULT_STATUS.value
            ).lower(),
        )
    except ValueError:
        raise InvalidConfiguration


def social_config_factory() -> SocialPostingConfig:
    """Factory function for dataclass ``SocialPostingConfig``

    :return: ``SocialPostingConfig``
    """
    try:
        section = ConfigSection.SOCIAL_POSTING.value
        return SocialPostingConfig(
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING_AUTO.value
            ),
            x_posting=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING.value
            ),
            telegram_sharing_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING_AUTO.value
            ),
            telegram_sharing=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.TELEGRAM_SHARING.value
            ),
            social_config_override=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.SOCIAL_CONFIG_OVERRIDE.value
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def image_config_factory() -> ImageConfig:
    """Factory function for dataclass ``ImageConfig``

    :return: ``ImageConfig``
    """

    try:
        section = ConfigSection.IMAGE_CONFIG.value
        return ImageConfig(
            img_seo_attrs=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.IMAGE_SEO_ATTRIBUTES.value
            ),
            pic_format=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.PICTURE_FORMAT.value
            ),
            imagick=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.IMAGICK_ENABLED.value
            ),
            img_conversion_quality=WORKFLOWS_CONFIG_INI.getint(
                section, ConfigOption.IMAGE_QUALITY.value
            ),
            pic_fallback=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.FALLBACK_PICTURE_FORMAT.value
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def ai_config_factory() -> AIServices:
    """
    Factory function for dataclass ``AIServices``

    :return: ``AIServices`` or None if configuration is invalid
    """
    try:
        section = ConfigSection.AI_CONFIG.value
        return AIServices(
            llm_provider=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.LLM_PROVIDER.value
            ),
            llm_model_tag=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.LLM_MODEL_TAG.value
            ),
            llm_serve_host=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.LLM_PROVIDER_HOST.value
            ),
            llm_serve_port=WORKFLOWS_CONFIG_INI.getint(
                section, ConfigOption.LLM_PROVIDER_PORT.value
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def content_bot_conf_factory() -> ContentBotConf:
    """Factory function for dataclass ``ContentBotConf``

    :return: ``ContentBotConf``
    """
    try:
        section = ConfigSection.CONTENT_BOT.value
        return ContentBotConf(
            sql_query=WORKFLOWS_CONFIG_INI.get(section, ConfigOption.SQL_QUERY.value),
            content_hint=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.DB_CONTENT_HINT.value
            ),
            assets_conf=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.ASSETS_CONF.value
            ),
            assets_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.ASSETS_ENABLED.value
            ),
            partners=WORKFLOWS_CONFIG_INI.get(section, ConfigOption.PARTNERS.value),
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING_AUTO.value
            ),
            x_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING.value
            ),
            telegram_sharing_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.TELEGRAM_SHARING_AUTO.value
            ),
            telegram_sharing_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.TELEGRAM_SHARING.value
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def gallery_bot_conf_factory() -> GalleryBotConf:
    """Factory function for dataclass ``EmbedAssistBotConf``

    :return: ``EmbedAssistBotConf``
    """
    try:
        section = ConfigSection.GALLERY_BOT.value
        return GalleryBotConf(
            content_hint=WORKFLOWS_CONFIG_INI.get(
                section,
                ConfigOption.DB_CONTENT_HINT.value,
            ),
            sql_query=WORKFLOWS_CONFIG_INI.get(section, ConfigOption.SQL_QUERY.value),
            partners=WORKFLOWS_CONFIG_INI.get(section, ConfigOption.PARTNERS.value),
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING_AUTO.value
            ),
            x_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING.value
            ),
            telegram_sharing_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section,
                ConfigOption.TELEGRAM_SHARING_AUTO.value,
            ),
            telegram_sharing_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section,
                ConfigOption.TELEGRAM_SHARING.value,
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def vid_embed_bot_conf_factory() -> EmbedAssistBotConf:
    """Factory function for dataclass ``EmbedAssistBotConf``

    :return: ``EmbedAssistBotConf``
    """
    try:
        section = ConfigSection.EMBED_ASSIST_BOT.value
        return EmbedAssistBotConf(
            sql_query=WORKFLOWS_CONFIG_INI.get(section, ConfigOption.SQL_QUERY.value),
            content_hint=WORKFLOWS_CONFIG_INI.get(
                section, ConfigOption.DB_CONTENT_HINT.value
            ),
            partners=WORKFLOWS_CONFIG_INI.get(section, ConfigOption.PARTNERS.value),
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING_AUTO.value
            ),
            x_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section, ConfigOption.X_POSTING.value
            ),
            telegram_sharing_auto=WORKFLOWS_CONFIG_INI.getboolean(
                section,
                ConfigOption.TELEGRAM_SHARING_AUTO.value,
            ),
            telegram_sharing_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                section,
                ConfigOption.TELEGRAM_SHARING.value,
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def feed_alpha_conf_factory() -> FeedAlphaConf:
    """
    Factory function for dataclass ``FeedAlphaConf``

    :return: ``FeedAlphaConf``
    """
    try:
        return FeedAlphaConf(
            campaign_id=WORKFLOWS_CONFIG_INI.getint(
                ConfigSection.FEED_ALPHA.value, ConfigOption.CAMPAIGN_ID.value
            )
        )
    except ValueError:
        raise InvalidConfiguration


def feed_beta_conf_factory() -> FeedBetaConf:
    """
    Factory function for dataclass ``FeedBetaConf``

    :return: ``FeedBetaConf``
    """
    try:
        return FeedBetaConf(
            source_id=WORKFLOWS_CONFIG_INI.getint(
                ConfigSection.FEED_BETA.value, ConfigOption.SOURCE_ID.value
            )
        )
    except ValueError:
        raise InvalidConfiguration


def feed_delta_conf_factory() -> FeedDeltaConf:
    """
    Factory function for dataclass ``FeedDeltaConf``

    :return: ``FeedDeltaConf``
    """
    try:
        return FeedDeltaConf(
            campaign_utm=WORKFLOWS_CONFIG_INI.get(
                ConfigSection.FEED_DELTA.value, ConfigOption.CAMPAIGN_UTM.value
            )
        )
    except ValueError:
        raise InvalidConfiguration


def web_sources_conf_factory() -> WebSourcesConf:
    """Factory function for dataclass ``TasksConf``

    :return: ``TasksConf``
    """
    try:
        return WebSourcesConf(
            feed_dump_url=WORKFLOWS_CONFIG_INI.get(
                ConfigSection.WEB_SOURCES.value, ConfigOption.FEED_DUMP_URL.value
            ),
            feed_set_url=WORKFLOWS_CONFIG_INI.get(
                ConfigSection.WEB_SOURCES.value, ConfigOption.FEED_SET_URL.value
            ),
            pw_api_base_url=WORKFLOWS_CONFIG_INI.get(
                ConfigSection.POST_WIZARD_API.value, ConfigOption.API_BASE_URL.value
            ),
        )
    except ValueError:
        raise InvalidConfiguration
