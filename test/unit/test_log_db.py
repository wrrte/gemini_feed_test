from storage.storage_sqlite import StorageManager
from storage.log_storage_sqlite import LogSqliteDB
from core.log.log import Log

from datetime import timezone, datetime, timedelta

def test_get_log_list():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    log_db = LogSqliteDB(storage_manager)

    logs = log_db.get_log_list()

    assert len(logs) == 0


def test_save_log_list():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    log_db = LogSqliteDB(storage_manager)

    log = Log()
    now = datetime.now(timezone(timedelta(hours=9)))
    log.date_time   = now 
    log.description = "dummy event"

    log_db.save_log(log)

    logs = log_db.get_log_list()

    assert len(logs) == 1
    assert logs[0].id == 1
    assert logs[0].date_time == now
    assert logs[0].description == "dummy event"

