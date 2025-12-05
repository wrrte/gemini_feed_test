from datetime import timezone, datetime, timedelta

from core.log.log import Log
from core.log.log_storage import ILogDB


class LogManager:
    def __init__(self, db: ILogDB):
        # self.logs = db.get_log_list() #Load all logs in memory
        self.db = db

    def save_log(self, log: Log):
        # self.logs.append(log)
        self.db.save_log(log)

    def get_log_list(self):
        return self.db.get_log_list()
        # return self.logs

    def get_time(self):
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        return now
