from core.setting.system_setting import SystemSettings
from core.setting.system_setting_storage import ISystemSettingsDB

import copy


class SystemSettingsMemoryDB(ISystemSettingsDB):
    def __init__(self):
        self.settings = SystemSettings()

    def update_system_settings(self, settings: SystemSettings):
        self.settings = copy.deepcopy(settings)

    def get_system_settings(self) -> SystemSettings:
        return copy.deepcopy(self.settings)
