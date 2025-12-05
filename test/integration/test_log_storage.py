from storage.storage_sqlite import StorageManager
from core.log.log_manager import LogManager
from storage.log_storage_sqlite import LogSqliteDB
from core.log.log import Log


def test_save_log():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    log_db = LogSqliteDB(storage_manager)
    log_manager = LogManager(log_db)

    now = log_manager.get_time()

    log = Log()
    log.date_time = now
    log.description = "dummy event"

    log_manager.save_log(log)

    assert log.id == 1


def test_save_and_get_log():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    log_db = LogSqliteDB(storage_manager)
    log_manager = LogManager(log_db)

    now = log_manager.get_time()

    log = Log()
    log.date_time = now
    log.description = "dummy event"

    log_manager.save_log(log)

    logs = log_manager.get_log_list()

    assert logs[-1].id == 1
    assert logs[-1].date_time == now
    assert logs[-1].description == "dummy event"
