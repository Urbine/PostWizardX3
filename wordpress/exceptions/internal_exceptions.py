"""
Internal Exceptions - WordPress
These are exceptions that are not meant to be raised by the user

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


class CacheSyncIntegrityError(Exception):
    """
    Notifies the user about failures in the HotFileSync process.
    Changes will not touch the wp_posts.json file if the config cannot be validated.
    In this case, you may want to investigate what went wrong, but it is way easier to
    rebuild the WordPress post caching and its config file.
    """

    def __init__(self):
        self.message = "WP JSON Cache Sync failed validation"
        super().__init__(self.message)


class MissingCacheError(Exception):
    """
    Alert users when the application is trying to update a cache file that does not exist.
    """

    def __init__(self, filename):
        self.message = f'Cache "{filename}" does not exist!'
        self.help = (
            "Connect to the internet when you call the WordPress constructor again"
        )
        super().__init__(f"{self.message}\n{self.help}")


class YoastSEOUnsupported(Exception):
    """
    Alert if Yoast Support is activated without having this plugin in their WordPress installation.
    """

    def __init__(self):
        self.message = (
            "This WordPress site does not have the Yoast SEO plugin installed"
        )
        self.help = "If you want, install the plugin in order to use the built-in support and delete the cache files."
        self.warning = "This plugin is not required to use this wrapper."
        super().__init__(f"{self.message}\n{self.help}\n{self.warning}")


class CacheCreationAuthError(Exception):
    """
    Alert users when the application fails to create a cache file due to a connection error or lack of permissions.
    This is determined when access-controlled headers are missing.
    """

    def __init__(self):
        self.message = (
            "WordPress cache creation failed. Check your credentials and try again."
        )
        self.help = "If you are getting this error, it is probably because you did not provide an app password for the site."
        self.link = "https://wordpress.com/support/security/two-step-authentication/application-specific-passwords/"
        super().__init__(
            f"{self.message}\n{self.help}\nFind more information here:\n{self.link}"
        )
