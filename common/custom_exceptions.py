class NoSuitableArgument(Exception):

    def __init__(self, message):
        """ This exception is used by functions that depend on CLI parameters.
        Raise if the expected parameters are not provided by the user.
        :param message:
        """
        super().__init__(message)

