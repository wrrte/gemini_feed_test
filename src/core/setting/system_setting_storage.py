from core.setting.system_setting import SystemSettings


class ISystemSettingsDB():
    def __init__(self):
        pass

    def update_system_settings(self, settings: SystemSettings):
        pass

    def get_system_settings(self) -> SystemSettings:
        pass
