from core.login.login_manager import LoginManager
from storage.password_storage_memory import PasswordMemoryDB
from storage.session_storage_memory import SessionMemoryDB
from storage.control_panel_setting_storage_memory import ControlPanelSettingsMemoryDB
from core.login.login_session import Session

import pytest
import time

def test_web_browser_log_in():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "1234", "TEST_WEB_BROWSER")
    assert result[0] == True

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "1234"
    assert answer.max_tries == 3
    assert answer.is_valid == True

def test_control_panel_master_log_in():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.cp_log_in("1234", "master")
    assert result[0] == True

    login_manager.cp_log_out()


def test_control_panel_guest_log_in():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.cp_log_in("", "guest")
    assert result[0] == True

    login_manager.cp_log_out()

def test_invalid_level_log_in():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    # Raising exception is the expected behavior
    with pytest.raises(Exception):
        login_manager.cp_log_in("1234", "admin")

def test_invalid_user_log_in():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("master", "1234", "TEST_WEB_BROWSER")
    assert result[0] == False

def test_web_log_in_failure():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "4321"
    assert answer.max_tries == 2
    assert answer.is_valid == False


def test_control_panel_guest_log_in_after_failure():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.cp_log_in("1234", "guest")
    assert result[0] == False

    result = login_manager.cp_log_in("", "guest")
    assert result[0] == True


def test_control_panel_log_in_failure_twice():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.cp_log_in("1234", "guest")
    assert result[0] == False
    result = login_manager.cp_log_in("1234", "guest")
    assert result[0] == False

def test_web_browser_log_in_success_after_failure():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)


    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "4321"
    assert answer.max_tries == 2
    assert answer.is_valid == False

    result = login_manager.web_log_in("admin", "1234", "TEST_WEB_BROWSER")
    assert result[0] == True

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "1234"
    assert answer.max_tries == 3
    assert answer.is_valid == True


def test_web_browser_log_in_failure_three_time():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "4321"
    assert answer.max_tries == 0
    assert answer.is_valid == False
    assert answer.lock_time != None


def test_web_browser_log_in_failure_four_time():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)
    login_manager.web_lockout = 1    

    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "4321"
    assert answer.max_tries == 0
    assert answer.is_valid == False
    assert answer.lock_time != None

def test_cp_log_in_failure_four_time():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)
    login_manager.cp_lockout = 1    

    result = login_manager.cp_log_in("4321", "master")
    assert result[0] == False
    result = login_manager.cp_log_in("4321", "master")
    assert result[0] == False
    result = login_manager.cp_log_in("4321", "master")
    assert result[0] == False
    result = login_manager.cp_log_in("1234", "master")
    assert result[0] == False

    assert login_manager.cp_lock_time != None


def test_log_in_after_lockout():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False
    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "4321"
    assert answer.max_tries == 0
    assert answer.is_valid == False
    assert answer.lock_time != None

    login_manager.web_lockout = 1    
    time.sleep(login_manager.web_lockout)    

    result = login_manager.web_log_in("admin", "1234", "TEST_WEB_BROWSER")
    assert result[0] == True

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "1234"
    assert answer.max_tries == 3
    assert answer.is_valid == True
    assert answer.lock_time == None

def test_cp_log_in_after_lockout():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)
    login_manager.cp_lockout = 1    

    result = login_manager.cp_log_in("4321", "master")
    assert result[0] == False
    result = login_manager.cp_log_in("4321", "master")
    assert result[0] == False
    result = login_manager.cp_log_in("4321", "master")
    assert result[0] == False

    time.sleep(login_manager.cp_lockout)    

    result = login_manager.cp_log_in("1234", "master")
    assert result[0] == True



def test_invalid_log_out():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    # Raising exception is the expected behavior
    with pytest.raises(Exception):
        login_manager.web_log_out("TEST_WEB_BROWSER")


def test_valid_log_out():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "1234", "TEST_WEB_BROWSER")
    assert result[0] == True

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer.user_id == "admin"
    assert answer.password == "1234"
    assert answer.max_tries == 3
    assert answer.is_valid == True
    assert answer.lock_time == None
  
    login_manager.web_log_out("TEST_WEB_BROWSER")

    answer = session_db.get_session_by_interface("TEST_WEB_BROWSER")
    assert answer == None

def test_cp_change_password_master():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    login_manager.cp_change_password("4321", "master")

    assert setting_db.get_master_password() == "4321"


def test_cp_change_password_guest():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    login_manager.cp_change_password("4321", "guest")

    assert setting_db.get_guest_password() == "4321"


def test_cp_change_password_exception():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    with pytest.raises(Exception):
        login_manager.cp_change_password("4321", "admin")


def test_web_change_password():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "1234", "TEST_WEB_BROWSER")
    assert result[0] == True

    login_manager.web_change_password("TEST_WEB_BROWSER", "4321")
    assert password_db.get_password("admin") == "4321"

def test_web_change_password_exception():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    result = login_manager.web_log_in("admin", "4321", "TEST_WEB_BROWSER")
    assert result[0] == False

    with pytest.raises(Exception):
        login_manager.web_change_password("TEST_WEB_BROWSER", "4321")

def test_web_change_password_exception2():
    password_db = PasswordMemoryDB()
    session_db = SessionMemoryDB()
    setting_db = ControlPanelSettingsMemoryDB()

    login_manager = LoginManager(password_db, session_db, setting_db)

    with pytest.raises(Exception):
        login_manager.web_change_password("TEST_WEB_BROWSER", "4321")

