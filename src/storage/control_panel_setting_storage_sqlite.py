from core.setting.control_panel_setting_storage import IControlPanelSettingsDB

import json

class ControlPanelSettingsSqliteDB(IControlPanelSettingsDB):
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager

    def get_master_password(self) -> str:
        query = """
        SELECT *
        FROM system_settings
        WHERE name = ?
        """
        rows = self.storage_manager.execute(query, ("master_password", ))

        if len(rows)==0:
            raise Exception("The master_password setting does not exist in DB")

        row = rows[0]

        json_value = json.loads(row[2])
 
        if "password" in json_value: 
            return json_value["password"]
        else:
            raise Exception("Wrong master_password json schema stored in DB")

    def set_master_password(self, new_password):
        query = """
        UPDATE system_settings
        SET value = ?
        WHERE name = ?
        """

        self.storage_manager.execute(query, (json.dumps({"password": new_password}), "master_password"))


    def get_guest_password(self) -> str:
        query = """
        SELECT *
        FROM system_settings
        WHERE name = ?
        """
        rows = self.storage_manager.execute(query, ("guest_password", ))

        if len(rows)==0:
            raise Exception("The guest_password setting does not exist in DB")

        row = rows[0]

        json_value = json.loads(row[2])
 
        if "password" in json_value: 
            return json_value["password"]
        else:
            raise Exception("Wrong guest_password json schema stored in DB")

    def set_guest_password(self, new_password):
        query = """
        UPDATE system_settings
        SET value = ?
        WHERE name = ?
        """

        self.storage_manager.execute(query, (json.dumps({"password": new_password}), "guest_password"))
