from core.setting.system_setting import SystemSettings
from core.setting.system_setting_storage import ISystemSettingsDB

import json


class SystemSettingsSqliteDB(ISystemSettingsDB):
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager

    def update_system_settings(self, settings: SystemSettings):
        query = """
        UPDATE system_settings
        SET value = ?
        WHERE name = ?
        """

        self.storage_manager.execute(
            query, (json.dumps({"time": settings.system_lock_time}), "system_lock_time"))
        self.storage_manager.execute(query,
                                     (json.dumps({"phone_number": settings.panic_phone_number}), "panic_phone_number"))
        self.storage_manager.execute(query, (
            json.dumps({"time": settings.alarm_time_before_phonecall}), "alarm_time_before_phonecall"))
        self.storage_manager.execute(query,
                                     (json.dumps({"phone_number": settings.home_phone_number}), "home_phone_number"))

    def get_system_settings(self) -> SystemSettings:
        query = """
        SELECT *
        FROM system_settings
        """
        rows = self.storage_manager.execute(query)

        json_values = {}

        for row in rows:
            json_values[row[1]] = json.loads(row[2])

        # print(json_values)

        settings = SystemSettings()
        if "system_lock_time" in json_values:
            if "time" in json_values["system_lock_time"]:
                settings.system_lock_time = json_values["system_lock_time"]["time"]
            else:
                raise Exception(
                    "Wrong system_lock_time json schema stored in DB")
        else:
            raise Exception(
                "Wrong json schema stored in DB. system_lock_time does not exist")

        if "panic_phone_number" in json_values:
            if "phone_number" in json_values["panic_phone_number"]:
                settings.panic_phone_number = json_values["panic_phone_number"]["phone_number"]
            else:
                raise Exception(
                    "Wrong panic_phone_number json schema stored in DB")
        else:
            raise Exception(
                "Wrong json schema stored in DB. panic_phone_number does not exist")

        if "alarm_time_before_phonecall" in json_values:
            if "time" in json_values["alarm_time_before_phonecall"]:
                settings.alarm_time_before_phonecall = json_values["alarm_time_before_phonecall"]["time"]
            else:
                raise Exception(
                    "Wrong alarm_time_before_phonecall json schema stored in DB")
        else:
            raise Exception(
                "Wrong json schema stored in DB. alarm_time_before_phonecall does not exist")

        if "home_phone_number" in json_values:
            if "phone_number" in json_values["home_phone_number"]:
                settings.home_phone_number = json_values["home_phone_number"]["phone_number"]
            else:
                raise Exception(
                    "Wrong home_phone_number json schema stored in DB")
        else:
            raise Exception(
                "Wrong json schema stored in DB. home_phone_number does not exist")

        return settings
