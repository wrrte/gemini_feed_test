from core.setting.control_panel_setting_storage import IControlPanelSettingsDB

class ControlPanelSettingsMemoryDB(IControlPanelSettingsDB):
    def __init__(self):
        self.master_password = "1234"
        self.guest_password  = ""

    def get_master_password(self) -> str:
        return self.master_password

    def set_master_password(self, new_password):
        self.master_password = new_password

    def get_guest_password(self) -> str:
        return self.guest_password

    def set_guest_password(self, new_password):
        self.guest_password = new_password
