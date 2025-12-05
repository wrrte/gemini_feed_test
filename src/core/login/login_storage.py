class ISessionDB:
    def __init__(self):
        pass

    def create_session(self, new_session):
        pass

    def update_session(self, new_session):
        pass

    def delete_session(self, interface):
        pass

    # returns invalid session by login interface
    def get_session_by_interface(self, interface):
        # shallow copy
        pass

    # returns valid session by id
    # def get_session_by_id(self, session_id):
    # shallow copy
    # pass
