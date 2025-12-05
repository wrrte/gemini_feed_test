from core.login.password_storage import IPasswordDB


class PasswordMemoryDB(IPasswordDB):
    def __init__(self):
        self.passwords = {}
        
        self.set_password("admin", "1234")

    def get_password(self, user_id):
        if user_id in self.passwords:
            return self.passwords[user_id]
        else:
            return None

    def set_password(self, user_id, new_password):
        self.passwords[user_id] = new_password
