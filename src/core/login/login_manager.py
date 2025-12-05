from core.login.login_session import Session
from core.login.password_storage import IPasswordDB
from core.login.login_storage import ISessionDB
from core.setting.control_panel_setting_storage import IControlPanelSettingsDB

from datetime import datetime, timedelta, timezone


class LoginManager:
    def __init__(self, password_db: IPasswordDB, session_db: ISessionDB, setting_db: IControlPanelSettingsDB):
        self.password_db   = password_db # password storage interface
        self.session_db    = session_db  # session storage interface
        self.setting_db    = setting_db

        # cp is abbreviation of control panel
        self.cp_max_tries  = 3
        self.cp_tries      = self.cp_max_tries
        self.cp_lockout    = 300
        self.cp_lock_time  = None
 
        self.web_max_tries = 3
        self.web_lockout   = 300

        self.timezone      = timezone(timedelta(hours=9))

    # Is it okay to place this here?
    def cp_change_password(self, new_password, level):
        if level == "master":
            self.setting_db.set_master_password(new_password)
        elif level == "guest":
            self.setting_db.set_guest_password(new_password)
        else:
            raise Exception("Unexpected login level")
    
    def cp_log_in(self, password, level):
        if self.cp_tries == 0:
            if self.cp_lock_time is None:
                raise Exception("lock time should not be None")

            now = datetime.now(self.timezone)
            if now > self.cp_lock_time + timedelta(seconds = self.cp_lockout):
                self.cp_tries = self.cp_max_tries
            else:
                time_left = int((timedelta(seconds = self.cp_lockout) - (now - self.cp_lock_time)).total_seconds())
                return (False, f"Lock time left: {time_left} seconds")

        if level == "master":
            correct_password = self.setting_db.get_master_password()
        elif level == "guest":
            correct_password = self.setting_db.get_guest_password()
        else:
            raise Exception("Unexpected login level")

        if password != correct_password:
            self.cp_tries -= 1

            if self.cp_tries == 0:
                self.cp_lock_time = datetime.now(self.timezone)

            return (False, "Wrong Password")
        else:
            self.cp_tries = self.cp_max_tries
            return (True, "")

    def cp_log_out(self):
        pass

    def web_change_password(self, interface, new_password):
        session = self.session_db.get_session_by_interface(interface)
        if session is None:
            raise Exception("No session exist")
        else:
            if session.is_valid:
                self.password_db.set_password(session.user_id, new_password)
            else:
                raise Exception("Invalid session tried to change password")

    def web_log_in(self, user_id, password, interface):
        session = self.session_db.get_session_by_interface(interface)
        if session is None:
            session = Session()

            session.user_id   = user_id
            session.password  = password
            session.interface = interface
            session.max_tries = self.web_max_tries
            session.is_valid  = password == self.password_db.get_password(user_id)

            self.session_db.create_session(session) # Should I return session id here?

            if session.is_valid:
                return (True, "")
            else:
                session.max_tries = session.max_tries - 1
                return (False, "Wrong id or password")
        else:
            if session.max_tries == 0 and session.lock_time is not None:
                now = datetime.now(self.timezone)
                if now > session.lock_time + timedelta(seconds=self.web_lockout):
                    session.max_tries = self.web_max_tries
                    session.lock_time = None
                else:
                    time_left = int((timedelta(seconds = self.web_lockout) - (now - session.lock_time)).total_seconds())
                    return (False, f"Lock time left: {time_left} seconds")

            session.user_id   = user_id
            session.password  = password
            session.interface = interface
            session.max_tries = session.max_tries - 1
            session.is_valid  = password == self.password_db.get_password(user_id)

            self.session_db.update_session(session)

            if session.is_valid:
                session.max_tries = self.web_max_tries
                return (True, "")
            else:
                if session.max_tries == 0:
                    session.lock_time = datetime.now(self.timezone)
                    return (False, f"Locked for {self.web_lockout} seconds")
                else:
                    return (False, "Wrong id or password")


    def web_log_out(self, interface):
        session = self.session_db.get_session_by_interface(interface)
        if session is None:
            raise Exception("No session exist")
        else:
            self.session_db.delete_session(interface)
