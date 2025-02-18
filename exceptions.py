class NotFoundError(Exception):
    pass


class MissingCriticalElementError(Exception):
    pass


class FuckedUpMarkupError(Exception):
    pass


class InvalidPagerTextError(ValueError):
    pass


class InvalidAvailabilityClassError(ValueError):
    pass


class MissingAvailabilityError(ValueError):
    pass


class MissingPriceError(ValueError):
    pass


class InvalidPriceError(ValueError):
    pass


class MissingTitleError(ValueError):
    pass
