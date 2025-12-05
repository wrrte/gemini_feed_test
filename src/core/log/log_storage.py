from core.log.log import Log


# Implementation of this interface either store in memory or in db.
class ILogDB:
    def __init__(self):
        pass

    def save_log(self, log: Log) -> None:
        pass

    def get_log_list(self) -> list[Log]:
        pass
