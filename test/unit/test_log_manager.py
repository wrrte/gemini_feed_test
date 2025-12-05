from core.log.log_manager import LogManager
from storage.log_storage_memory import LogMemoryDB
from core.log.log import Log


def test_save_log():
    log_db = LogMemoryDB()
    log_manager = LogManager(log_db)

    now = log_manager.get_time()

    log = Log()
    log.date_time = now
    log.description = "dummy event"

    log_manager.save_log(log)

    assert log_db.logs[-1].id == 0
    assert log_db.logs[-1].date_time == now
    assert log_db.logs[-1].description == "dummy event"


def test_get_log():
    log_db = LogMemoryDB()
    log_manager = LogManager(log_db)

    now = log_manager.get_time()

    log = Log()
    log.date_time = now
    log.description = "dummy event"

    log_manager.save_log(log)

    assert log_db.logs[-1].id == 0
    assert log_db.logs[-1].date_time == now
    assert log_db.logs[-1].description == "dummy event"

    logs = log_manager.get_log_list()

    assert logs[-1].id == 0
    assert logs[-1].date_time == now
    assert logs[-1].description == "dummy event"
