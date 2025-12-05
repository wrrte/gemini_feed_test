from core.login.login_storage import ISessionDB


class SessionMemoryDB(ISessionDB):
    def __init__(self):
        self.sessions = {}

    def create_session(self, new_session):
        self.sessions[new_session.interface] = new_session

    def update_session(self, new_session):
        self.sessions[new_session.interface] = new_session

    def delete_session(self, interface):
        if interface in self.sessions:
            del self.sessions[interface]
        else:
            raise Exception("No session to delete for given interface")

    # returns invalid session by login interface
    def get_session_by_interface(self, interface):
        if interface in self.sessions:
            return self.sessions[interface]
        else:
            return None

    # returns valid session by id
    # def get_session_by_id(self, session_id):
    # shallow copy
    # pass
