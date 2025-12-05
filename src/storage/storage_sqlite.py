import sqlite3
import os


class StorageManager:
    def __init__(self, init_script_path, db_file_path):
        self.init_script_path = init_script_path
        self.db_file_path = db_file_path

        if not os.path.exists(self.db_file_path):
            try:
                with open(self.init_script_path, "r", encoding='utf-8') as f:
                    sql_script = f.read()

                conn = sqlite3.connect(self.db_file_path)
                try:
                    cur = conn.cursor()

                    cur.executescript(sql_script)
                    conn.commit()
                finally:
                    conn.close()
            except Exception as e:
                print(f"storage manager - while init: {e}")
        else:
            pass

    def reset(self):
        try:
            os.remove(self.db_file_path)

            with open(self.init_script_path, "r", encoding='utf-8') as f:
                sql_script = f.read()

            conn = sqlite3.connect(self.db_file_path)
            try:
                cur = conn.cursor()

                cur.executescript(sql_script)
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            print(f"storage manger - while reset: {e}")

    def execute(self, query, params=()):
        conn = sqlite3.connect(self.db_file_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            cur = conn.cursor()

            cur.execute(query, params)
            rows = cur.fetchall()

            conn.commit()
            conn.close()

            return rows
        finally:
            conn.close()

    def execute_insert(self, query, params=()):
        conn = sqlite3.connect(self.db_file_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            cur = conn.cursor()

            cur.execute(query, params)
            new_id = cur.lastrowid

            conn.commit()
            conn.close()

            return new_id
        finally:
            conn.close()
