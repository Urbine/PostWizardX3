
class NoSuitableArgument(Exception):
    """
    Used by functions that depend on CLI parameters.
    Raise if the expected parameters are not provided by the user.
    """

    def __init__(self, message):
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
        self.message = 'The input you have provided is not valid. Double check it and re-run.'
        super().__init__(self.message)