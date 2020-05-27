class OnboardApiException(Exception):
    """Wrapper for exceptions throw by the API client"""
    pass


class OnboardTemporaryException(OnboardApiException):
    """These exceptions indicate that a call failed in a temporary manner
    and should be retried
    """
    pass
