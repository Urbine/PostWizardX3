class NoSuitableArgument(Exception):
    """
    Used by functions that depend on CLI parameters.
    Raise if the expected parameters are not provided by the user.
    """

    def __init__(self, message: str):
        """
        :param message: text provided to the constructor by the user.
        """
        super().__init__(message)


class InvalidInput(Exception):
    """
    Used by functions that depend on user input.
    Raise if the expected values are not provided via user input.
    """

    def __init__(self):
        self.message = (
            "The input you have provided is not valid. Double check it and re-run."
        )
        super().__init__(self.message)


class ConfigFileNotFound(Exception):
    """
    Deal with instances where a configuration file does not exist.
    If this happens, you may want to check the filename or create the configuration
    file according to the needs of the project.

    """
    def __init__(self, filename: str):
        self.filename = filename
        self.message = (
            f"Filename {filename} does not exist. Create it if you haven't already."
        )
        super().__init__(self.message)
