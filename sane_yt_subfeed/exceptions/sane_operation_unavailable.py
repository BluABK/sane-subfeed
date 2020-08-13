class SaneOperationUnavailable(Exception):
    def __init__(self, message, exceptions=None):
        """
        Exception thrown for unavailable operations,
        which is usually thrown if a signal can't be connected.
        :param message:
        :param exceptions:
        """

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Bundle in any exceptions that occurred during the operation.
        if exceptions:
            self.exceptions = exceptions
            self.exc_count = len(exceptions)
