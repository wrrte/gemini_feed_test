from core.setting.system_setting import SystemSettings
from core.setting.system_setting_storage import ISystemSettingsDB


class SystemSettingsManager:
    def __init__(self, system_settings_db: ISystemSettingsDB):
        self.system_settings_db = system_settings_db
        self.settings = system_settings_db.get_system_settings()

    def update_system_settings(self, settings: SystemSettings):
        self.settings = settings
        self.system_settings_db.update_system_settings(settings)

    def get_system_settings(self) -> SystemSettings:
        return self.settings
