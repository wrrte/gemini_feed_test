class SecurityException(Exception):
    pass


class SensorNotFoundError(SecurityException):
    pass


class SensorAlreadyExistsError(SecurityException):
    pass


class SecurityZoneNotFoundError(SecurityException):
    pass


class SecurityModeNotFoundError(SecurityException):
    pass


class SecurityModeAlreadyExistsError(SecurityException):
    pass
