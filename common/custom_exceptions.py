class NoSuitableArgument(Exception):
    """Used by functions that depend on CLI parameters.
    Raise if the expected parameters are not provided by the user.
    """

    def __init__(self, message):
        """
        :param message: text provided to the constructor by the user.
        """
        super().__init__(message)
