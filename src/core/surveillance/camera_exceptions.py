class CameraError(Exception):
    """Base class for camera-related errors."""


class CameraAlreadyExistsError(CameraError):
    """Raised when trying to create a camera with an existing id."""


class CameraNotFoundError(CameraError):
    """Raised when the requested camera does not exist."""


class InvalidLocationError(CameraError):
    """Raised when a camera location is invalid (e.g. negative coordinates)."""


class CameraDisabledError(CameraError):
    """Raised when an operation requires an enabled camera."""


class InvalidStepError(CameraError):
    """Raised when a zoom or pan step is not a positive integer."""


class InvalidPasswordError(CameraError):
    """Raised when a camera password check fails."""
