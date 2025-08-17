"""
Config Writer Module
This module provides functions to write configuration options to the ``workflows_config.ini`` file.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Callable, get_type_hints

# Local implementation
from core.models.file_system import ApplicationPath, ProjectFile
from core.utils.file_system import write_config_file
from core.exceptions.util_exceptions import UnsupportedConfigArgument
from core.models.config_model import ConfigOption, ConfigSection


class ConfigWriter:
    """
    Class for writing configuration options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Utility class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_entry(
        section: ConfigSection, option: ConfigOption, value: str | bool | int
    ) -> bool:
        """
        Generic function to write a configuration option to the ``workflows_config.ini`` file.

        :param section: ``ConfigSection`` -> The section of the configuration file.
        :param option: ``ConfigOption`` -> The specific configuration option to write.
        :param value: ``str`` -> The value to set for the configuration option.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        return write_config_file(
            ProjectFile.WORKFLOWS_CONFIG.value,
            ApplicationPath.CONFIG_PKG.value,
            section.value,
            option.value,
            value,
        )

    @staticmethod
    def config_validate(writer_func: Callable, /, *args) -> None:
        """
        Validate the arguments passed to a configuration writing function.
        The function checks if the number of arguments matches the number of arguments in the function signature,
        and if the types of the arguments match the types specified in the function signature to avoid potential
        corruption of the configuration file.

        :param writer_func: ``Callable`` -> The function to validate.
        :param args: ``Iterable[Any]`` -> The arguments to validate.
        :return: ``None``
        """
        args_annotations = {
            var: typ
            for var, typ in get_type_hints(writer_func).items()
            if var != "return"
        }
        if len(args_annotations.keys()) == len(args):
            for p_arg, typ, arg in zip(
                args_annotations.keys(), args_annotations.values(), args
            ):
                if isinstance(arg, typ):
                    continue
                else:
                    raise UnsupportedConfigArgument(
                        f"Argument {p_arg} with value {arg} has type {type(arg)} instead of {typ} for {writer_func.__name__}"
                    )
            return None
        else:
            raise UnsupportedConfigArgument(
                f"Function {writer_func.__name__} has {len(args_annotations.keys())} arguments: {args_annotations} -> instead of {len(args)} arguments: {args}"
            )


class GeneralConfig:
    """
    Class for writing general configuration options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_website_name(value: str) -> bool:
        """
        Write the website name to the configuration file.

        :param value: ``str`` -> The name of the website to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(GeneralConfig.write_website_name, value)
        return ConfigWriter.write_entry(
            ConfigSection.GENERAL_CONFIG, ConfigOption.WEBSITE_NAME, value
        )

    @staticmethod
    def write_fqdomain_name(value: str) -> bool:
        """
        Write the fully qualified domain name to the configuration file.

        :param value: ``str`` -> The fully qualified domain name to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(GeneralConfig.write_fqdomain_name, value)
        return ConfigWriter.write_entry(
            ConfigSection.GENERAL_CONFIG, ConfigOption.FQDOMAIN_NAME, value
        )

    @staticmethod
    def write_enable_logging(value: bool) -> bool:
        """
        Write the enable logging option to the configuration file.

        :param value: ``str`` -> The value to set for enabling logging (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(GeneralConfig.write_enable_logging, value)
        return ConfigWriter.write_entry(
            ConfigSection.GENERAL_CONFIG, ConfigOption.ENABLE_LOGGING, value
        )

    @staticmethod
    def write_default_status(value: str) -> bool:
        """
        Write the default status for posts to the configuration file.

        :param value: ``str`` -> The default status to set (e.g., ``Draft`` or ``Publish``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(GeneralConfig.write_default_status, value)
        return ConfigWriter.write_entry(
            ConfigSection.GENERAL_CONFIG, ConfigOption.DEFAULT_STATUS, value
        )


class SocialConfig:
    """
    Class for writing social media posting/sharing configuration options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_x_posting_auto(value: bool) -> bool:
        """
        Write the auto posting option for X (formerly Twitter) to the configuration file.

        :param value: ``bool`` -> The value to set for auto posting (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(SocialConfig.write_x_posting_auto, value)
        return ConfigWriter.write_entry(
            ConfigSection.SOCIAL_POSTING, ConfigOption.X_POSTING_AUTO, value
        )

    @staticmethod
    def write_telegram_sharing_auto(value: bool) -> bool:
        """
        Write the auto sharing option for Telegram to the configuration file.

        :param value: ``bool`` -> The value to set for auto sharing (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(SocialConfig.write_telegram_sharing_auto, value)
        return ConfigWriter.write_entry(
            ConfigSection.SOCIAL_POSTING, ConfigOption.TELEGRAM_SHARING_AUTO, value
        )

    @staticmethod
    def write_x_social_posting(value: bool) -> bool:
        """
        Write the X (formerly Twitter) social posting option to the configuration file.

        :param value: ``str`` -> The value to set for X social posting (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(SocialConfig.write_x_social_posting, value)
        return ConfigWriter.write_entry(
            ConfigSection.SOCIAL_POSTING, ConfigOption.X_POSTING, value
        )

    @staticmethod
    def write_telegram_sharing(value: bool) -> bool:
        """
        Write the Telegram sharing option to the configuration file.

        :param value: str -> The value to set for Telegram sharing (e.g., ``True`` or ``False``).
        :return: bool -> True if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(SocialConfig.write_telegram_sharing, value)
        return ConfigWriter.write_entry(
            ConfigSection.SOCIAL_POSTING, ConfigOption.TELEGRAM_SHARING, value
        )

    @staticmethod
    def write_social_config_override(value: bool) -> bool:
        """
        Write the social config override option to the configuration file.

        :param value: ``str`` -> The value to set for social config override (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(SocialConfig.write_social_config_override, value)
        return ConfigWriter.write_entry(
            ConfigSection.SOCIAL_POSTING, ConfigOption.SOCIAL_CONFIG_OVERRIDE, value
        )


class ImageConfig:
    """
    Class for writing image optimization options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_image_seo_attributes(value: bool) -> bool:
        """
        Write the image SEO attributes option to the configuration file.

        :param value: ``str`` -> The value to set for image SEO attributes (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(ImageConfig.write_image_seo_attributes, value)
        return ConfigWriter.write_entry(
            ConfigSection.IMAGE_CONFIG, ConfigOption.IMAGE_SEO_ATTRIBUTES, value
        )

    @staticmethod
    def write_picture_format(value: str) -> bool:
        """
        Write the preferred picture format for posts to the configuration file.

        :param value: ``str`` -> The preferred picture format to set (e.g., "jpg", "png").
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(ImageConfig.write_picture_format, value)
        return ConfigWriter.write_entry(
            ConfigSection.IMAGE_CONFIG, ConfigOption.PICTURE_FORMAT, value
        )

    @staticmethod
    def write_image_quality(value: int) -> bool:
        """
        Write the image quality setting to the configuration file.

        :param value: ``str`` -> The image quality to set (e.g., "80" for 80% quality).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(ImageConfig.write_image_quality, value)
        return ConfigWriter.write_entry(
            ConfigSection.IMAGE_CONFIG, ConfigOption.IMAGE_QUALITY, value
        )

    @staticmethod
    def write_fallback_picture_format(value: str) -> bool:
        """
        Write the fallback picture format for posts to the configuration file.

        :param value: ``str`` -> The fallback picture format to set (e.g., ``jpg``, ``png``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(ImageConfig.write_fallback_picture_format, value)
        return ConfigWriter.write_entry(
            ConfigSection.IMAGE_CONFIG, ConfigOption.FALLBACK_PICTURE_FORMAT, value
        )

    @staticmethod
    def write_imagick_enabled(value: bool) -> bool:
        """
        Write the ImageMagick enabled option to the configuration file.

        :param value: ``str`` -> The value to set for ImageMagick enabled (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(ImageConfig.write_imagick_enabled, value)
        return ConfigWriter.write_entry(
            ConfigSection.IMAGE_CONFIG, ConfigOption.IMAGICK_ENABLED, value
        )


class AIConfig:
    """
    Class for writing AI provider and model options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_llm_model_tag(value: str) -> bool:
        """
        Write the LLM model tag to the configuration file.

        :param value: ``str`` -> The tag of the LLM model to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(AIConfig.write_llm_model_tag, value)
        return ConfigWriter.write_entry(
            ConfigSection.AI_CONFIG, ConfigOption.LLM_MODEL_TAG, value
        )

    @staticmethod
    def write_llm_provider(value: str) -> bool:
        """
        Write the LLM provider to the configuration file.

        :param value: ``str`` -> The name of the LLM provider to set (e.g., ``Ollama``, ``LMStudio``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(AIConfig.write_llm_provider, value)
        return ConfigWriter.write_entry(
            ConfigSection.AI_CONFIG, ConfigOption.LLM_PROVIDER, value
        )

    @staticmethod
    def write_llm_provider_host(value: str) -> bool:
        """
        Write the LLM provider host to the configuration file.

        :param value: ``str`` -> The hostname or address of the LLM provider to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, False otherwise.
        """
        ConfigWriter.config_validate(AIConfig.write_llm_provider_host, value)
        return ConfigWriter.write_entry(
            ConfigSection.AI_CONFIG, ConfigOption.LLM_PROVIDER_HOST, value
        )

    @staticmethod
    def write_llm_port(value: int) -> bool:
        """
        Write the LLM provider port to the configuration file.

        :param value: ``str`` -> The port number of the LLM provider to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(AIConfig.write_llm_port, value)
        return ConfigWriter.write_entry(
            ConfigSection.AI_CONFIG, ConfigOption.LLM_PROVIDER_PORT, value
        )


class MCashContentBotConfig(SocialConfig):
    """
    Class for writing the MongerCash Content Bot configuration options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_partner_names(partners: str) -> bool:
        """
        Write the partner names to the configuration file.

        :param partners: ``Iterable[str]`` -> The names of the partners to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(
            MCashContentBotConfig.write_partner_names, partners
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.PARTNERS, partners
        )

    @staticmethod
    def write_mcash_db_query(sql_query: str) -> bool:
        """
        Write the MongerCash video database query to the configuration file.

        :param sql_query: ``str`` -> The SQL query to set.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(
            MCashContentBotConfig.write_mcash_db_query, sql_query
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.SQL_QUERY, sql_query
        )

    @staticmethod
    def write_assets_enabled(value: bool) -> bool:
        """
        Write the assets enabled option to the configuration file.

        :param value: ``str`` -> The value to set for assets enabled (e.g., ``True`` or ``False``).
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(MCashContentBotConfig.write_assets_enabled, value)
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.ASSETS_ENABLED, value
        )

    @staticmethod
    def write_telegram_sharing(value: bool) -> bool:
        ConfigWriter.config_validate(
            MCashContentBotConfig.write_telegram_sharing, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.TELEGRAM_SHARING, value
        )

    @staticmethod
    def write_x_posting_auto(value: bool) -> bool:
        ConfigWriter.config_validate(MCashContentBotConfig.write_x_posting_auto, value)
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.X_POSTING_AUTO, value
        )

    @staticmethod
    def write_telegram_sharing_auto(value: bool) -> bool:
        ConfigWriter.config_validate(
            MCashContentBotConfig.write_telegram_sharing_auto, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.TELEGRAM_SHARING_AUTO, value
        )

    @staticmethod
    def write_x_social_posting(value: bool) -> bool:
        ConfigWriter.config_validate(
            MCashContentBotConfig.write_x_social_posting, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_CONTENT_BOT, ConfigOption.X_POSTING, value
        )


class MCashGalleryBotConfig(MCashContentBotConfig):
    """
    Class for writing the MongerCash Gallery Bot configuration options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_partner_names(partners: str) -> bool:
        ConfigWriter.config_validate(
            MCashGalleryBotConfig.write_partner_names, partners
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_GALLERY_BOT, ConfigOption.PARTNERS, partners
        )

    @staticmethod
    def write_mcash_db_query(sql_query: str) -> bool:
        ConfigWriter.config_validate(
            MCashGalleryBotConfig.write_mcash_db_query, sql_query
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_GALLERY_BOT, ConfigOption.SQL_QUERY, sql_query
        )

    @staticmethod
    def write_telegram_sharing(value: bool) -> bool:
        ConfigWriter.config_validate(
            MCashGalleryBotConfig.write_telegram_sharing, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_GALLERY_BOT, ConfigOption.TELEGRAM_SHARING, value
        )

    @staticmethod
    def write_x_posting_auto(value: bool) -> bool:
        ConfigWriter.config_validate(MCashGalleryBotConfig.write_x_posting_auto, value)
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_GALLERY_BOT, ConfigOption.X_POSTING_AUTO, value
        )

    @staticmethod
    def write_telegram_sharing_auto(value: bool) -> bool:
        ConfigWriter.config_validate(
            MCashGalleryBotConfig.write_telegram_sharing_auto, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_GALLERY_BOT, ConfigOption.TELEGRAM_SHARING_AUTO, value
        )

    @staticmethod
    def write_x_social_posting(value: bool) -> bool:
        ConfigWriter.config_validate(
            MCashGalleryBotConfig.write_x_social_posting, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.MCASH_GALLERY_BOT, ConfigOption.X_POSTING, value
        )


class VidEmbedAssistBotConfig(MCashContentBotConfig):
    """
    Class for writing the Embed Assist Bot configuration options to the ``workflows_config.ini`` file.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_partner_names(partners: str) -> bool:
        ConfigWriter.config_validate(
            VidEmbedAssistBotConfig.write_partner_names, partners
        )
        return ConfigWriter.write_entry(
            ConfigSection.EMBED_ASSIST_BOT, ConfigOption.PARTNERS, partners
        )

    @staticmethod
    def write_mcash_db_query(sql_query: str) -> bool:
        ConfigWriter.config_validate(
            VidEmbedAssistBotConfig.write_mcash_db_query, sql_query
        )
        return ConfigWriter.write_entry(
            ConfigSection.EMBED_ASSIST_BOT, ConfigOption.SQL_QUERY, sql_query
        )

    @staticmethod
    def write_telegram_sharing(value: bool) -> bool:
        ConfigWriter.config_validate(
            VidEmbedAssistBotConfig.write_telegram_sharing, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.EMBED_ASSIST_BOT, ConfigOption.TELEGRAM_SHARING, value
        )

    @staticmethod
    def write_x_posting_auto(value: bool) -> bool:
        ConfigWriter.config_validate(
            VidEmbedAssistBotConfig.write_x_posting_auto, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.EMBED_ASSIST_BOT, ConfigOption.X_POSTING_AUTO, value
        )

    @staticmethod
    def write_telegram_sharing_auto(value: bool) -> bool:
        ConfigWriter.config_validate(
            VidEmbedAssistBotConfig.write_telegram_sharing_auto, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.EMBED_ASSIST_BOT, ConfigOption.TELEGRAM_SHARING_AUTO, value
        )

    @staticmethod
    def write_x_social_posting(value: bool) -> bool:
        ConfigWriter.config_validate(
            VidEmbedAssistBotConfig.write_x_social_posting, value
        )
        return ConfigWriter.write_entry(
            ConfigSection.EMBED_ASSIST_BOT, ConfigOption.X_POSTING, value
        )


class AdultNextFeedConfig:
    """
    Class for writing configuration options related to the AdultNext feed.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_campaign_id(campaign_id: int) -> bool:
        """
        Write the campaign ID to the configuration file.

        :param campaign_id: ``int`` -> The campaign ID to write.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(AdultNextFeedConfig.write_campaign_id, campaign_id)
        return ConfigWriter.write_entry(
            ConfigSection.ADULT_NEXT_FEED, ConfigOption.CAMPAIGN_ID, campaign_id
        )


class TubeCorpFeedConfig:
    """
    Class for writing configuration options related to the TubeCorp feed.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_source_id(source_id: int) -> bool:
        """
        Write the source ID to the configuration file.

        :param source_id: ``int`` -> The source ID to write.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(TubeCorpFeedConfig.write_source_id, source_id)
        return ConfigWriter.write_entry(
            ConfigSection.TUBECORP_FEED, ConfigOption.SOURCE_ID, source_id
        )


class FHouseFeedConfig:
    """
    Class for writing configuration options related to the FHouse feed.
    """

    def __new__(cls):
        raise TypeError(f"Class {cls.__name__} cannot be instantiated.")

    @staticmethod
    def write_campaign_utm(campaign_utm: str) -> bool:
        """
        Write the source ID to the configuration file.

        :param campaign_utm: ``str`` -> The source ID to write.
        :return: ``bool`` -> ``True`` if the write operation was successful, ``False`` otherwise.
        """
        ConfigWriter.config_validate(FHouseFeedConfig.write_campaign_utm, campaign_utm)
        return ConfigWriter.write_entry(
            ConfigSection.FHOUSE_FEED, ConfigOption.CAMPAIGN_UTM, campaign_utm
        )
