from core.log.log import Log
from core.log.log_storage import ILogDB

from datetime import datetime


class LogSqliteDB(ILogDB):
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager

    def save_log(self, log: Log):
        query = """
        INSERT INTO "logs" ("date_time", "description") VALUES (?, ?);
        """
        log.id = self.storage_manager.execute_insert(query, (log.date_time.isoformat(" "), log.description))

    def get_log_list(self):
        query = """
        SELECT *
        FROM logs
        """
        rows = self.storage_manager.execute(query)

        logs = []

        for row in rows:
            log = Log()
            log.id = row[0]
            log.date_time = datetime.fromisoformat(row[1])
            log.description = row[2]
            logs.append(log)

        return logs
