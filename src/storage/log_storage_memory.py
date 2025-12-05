
from core.log.log import Log
from core.log.log_storage import ILogDB

import copy


# Implementation of this interface either store in memory or in db.
class LogMemoryDB(ILogDB):
    def __init__(self):
        self.logs = []

    def save_log(self, log: Log):
        log.id = len(self.logs)
        self.logs.append(copy.deepcopy(log))

    def get_log_list(self):
        return copy.deepcopy(self.logs)
