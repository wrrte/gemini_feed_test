from abc import ABC, abstractmethod

from core.security.security_zone_geometry.area import Area


class InterfaceSensor(ABC):
    def __init__(self):
        self.armed: bool = False
        self.area: Area | None = None

    @abstractmethod
    def get_id(self):
        raise NotImplementedError

    @abstractmethod
    def read(self):
        raise NotImplementedError

    @abstractmethod
    def arm(self):
        raise NotImplementedError

    @abstractmethod
    def disarm(self):
        raise NotImplementedError

    @abstractmethod
    def test_armed_state(self):
        raise NotImplementedError
