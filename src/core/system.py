from core.log.log_manager import LogManager
from core.login.login_manager import LoginManager
from core.security.security_manager import SecurityManager
from core.setting.system_setting_manager import SystemSettingsManager
from core.surveillance.camera_controller import CameraController

from core.security.security_memory_database import SecurityMemoryDatabase
from storage.camera_storage_memory import CameraMemoryDB
from storage.log_storage_memory import LogMemoryDB
from storage.password_storage_memory import PasswordMemoryDB
from storage.session_storage_memory import SessionMemoryDB
from storage.system_setting_storage_memory import SystemSettingsMemoryDB
from storage.control_panel_setting_storage_memory import ControlPanelSettingsMemoryDB

from storage.storage_sqlite import StorageManager
from storage.camera_storage_sqlite import CameraSqliteDB
from storage.log_storage_sqlite import LogSqliteDB
from storage.password_storage_sqlite import PasswordSqliteDB
from storage.security_storage_sqlite import SecuritySqliteDB
from storage.system_setting_storage_sqlite import SystemSettingsSqliteDB
from storage.control_panel_setting_storage_sqlite import ControlPanelSettingsSqliteDB

system_use_db = True


class System:

    def __init__(self, use_db: bool) -> None:
        self.on = False
        self.current_control_panel = None
        self.current_app = None
        self.use_db = use_db

        self._poll_after_id = None
        self._call_pending = False

        self.storage_manager = StorageManager("src/init.sql", "safehome.db")

        if self.use_db:
            self.settings_db = SystemSettingsSqliteDB(self.storage_manager)
            self.camera_db = CameraSqliteDB(self.storage_manager)
            self.current_log_db = LogSqliteDB(self.storage_manager)
            self.security_db = SecuritySqliteDB(self.storage_manager)
            self.password_db = PasswordSqliteDB(self.storage_manager)
            self.cp_settings_db = ControlPanelSettingsSqliteDB(
                self.storage_manager)
        else:
            self.settings_db = SystemSettingsMemoryDB()
            self.camera_db = CameraMemoryDB()
            self.current_log_db = LogMemoryDB()
            self.security_db = SecurityMemoryDatabase()
            self.password_db = PasswordMemoryDB()
            self.cp_settings_db = ControlPanelSettingsMemoryDB()

        self.session_db = SessionMemoryDB()

        self.current_system_settings_manager = SystemSettingsManager(
            self.settings_db)

        self.current_camera_controller = CameraController(self.camera_db)
        if not use_db:
            self.current_camera_controller.add_camera(
                camera_id=1, location=(110, 50))
            self.current_camera_controller.add_camera(
                camera_id=2, location=(220, 180), password="1234")
            self.current_camera_controller.add_camera(
                camera_id=3, location=(390, 250))

        self.current_log_manager = LogManager(self.current_log_db)
        self.current_security_manager = SecurityManager(
            self.security_db, self.current_log_manager)
        self.login_manager = LoginManager(
            self.password_db, self.session_db, self.cp_settings_db)

    def _poll_loop(self):
        if not self.on:
            return

        self.poll_sensors()

        if self.current_app:
            self._poll_after_id = self.current_app.after(200, self._poll_loop)

    def turn_on(self):
        self.on = True
        if self.current_app:
            self.current_app.back_to_login()
            self.current_app.deiconify()
            self.current_app.lift()
            if self._poll_after_id is None:
                self._poll_loop()
        else:
            raise Exception("no web gui found")

    def turn_off(self):
        self.on = False
        if self._poll_after_id and self.current_app:
            try:
                self.current_app.after_cancel(self._poll_after_id)
            except Exception as e:
                print("Error cancelling poll loop:", e)
        self._poll_after_id = None
        if self.current_app:
            self.current_app.withdraw()
        else:
            raise Exception("no web gui found")

    def reset(self):
        self.storage_manager.reset()
        self.session_db = SessionMemoryDB()

        self.current_system_settings_manager = SystemSettingsManager(
            self.settings_db)

        self.current_camera_controller = CameraController(self.camera_db)
        if not self.use_db:
            self.current_camera_controller.add_camera(
                camera_id=1, location=(110, 50))
            self.current_camera_controller.add_camera(
                camera_id=2, location=(220, 180), password="1234")
            self.current_camera_controller.add_camera(
                camera_id=3, location=(390, 250))

        self.current_log_manager = LogManager(self.current_log_db)
        self.current_security_manager = SecurityManager(
            self.security_db, self.current_log_manager)
        self.login_manager = LoginManager(
            self.password_db, self.session_db, self.cp_settings_db)

    def poll_sensors(self):
        (_, armed_detected) = self.current_security_manager.update(True)
        if armed_detected:
            string_armed_detected = str([s.get_id() for s in armed_detected])
            if self.current_control_panel:
                self.current_control_panel.set_display_short_message1(
                    "SENSOR INTRUSION: " + string_armed_detected)
                self.current_control_panel.set_armed_led(True)
            self.make_panic_phone_call()

    def make_panic_phone_call(self):
        if self._call_pending:
            return
        self._call_pending = True
        settings = system.current_system_settings_manager.get_system_settings()
        phone = settings.panic_phone_number
        delay_seconds = int(settings.alarm_time_before_phonecall)
        self._call_countdown(delay_seconds, phone)

    def _call_countdown(self, seconds_left, phone_number):
        if seconds_left > 0:
            if self.current_control_panel:
                self.current_control_panel.set_display_short_message2(
                    f"Calling {phone_number} in {seconds_left}..."
                )

            if self.current_app:
                self.current_app.after(1000, lambda: self._call_countdown(seconds_left - 1, phone_number))
            return

        # finish
        if self.current_control_panel:
            self.current_control_panel.set_display_short_message2(
                f"Called {phone_number}"
            )
            self.current_control_panel.set_armed_led(False)

        self._call_pending = False


system = System(system_use_db)
