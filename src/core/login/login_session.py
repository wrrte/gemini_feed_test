# corresponds to LoginInterface in SDS
class Session:
    def __init__(self):
        self.__user_id = None  # user_id that user entered
        self.__password = None  # password that user entered
        self.__interface = None  # interface(eg. control panel) for log in
        self.__max_tries = None  # maximum number of retry
        self.__lock_time = None  # timestamp of initial lock
        # self.__session_id = None  # session id 
        self.__is_valid = False  # boolean representing whether session is valid

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, new_user_id):
        self.__user_id = new_user_id
        return self.__user_id

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, new_password):
        self.__password = new_password
        return self.__password

    @property
    def interface(self):
        return self.__interface

    @interface.setter
    def interface(self, new_interface):
        self.__interface = new_interface
        return self.__interface

    @property
    def max_tries(self):
        return self.__max_tries

    @max_tries.setter
    def max_tries(self, new_max_tries):
        self.__max_tries = new_max_tries
        return self.__max_tries

    @property
    def lock_time(self):
        return self.__lock_time

    @lock_time.setter
    def lock_time(self, new_lock_time):
        self.__lock_time = new_lock_time
        return self.__lock_time

#    @property
#    def session_id(self):
#        return self.__session_id

#    @session_id.setter
#    def id(self, new_session_id):
#        self.__session_id = new_session_id
#        return self.__session_id

    @property
    def is_valid(self):
        return self.__is_valid

    @is_valid.setter
    def is_valid(self, new_is_valid):
        self.__is_valid = new_is_valid
        return self.__is_valid
