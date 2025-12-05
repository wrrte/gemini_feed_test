class Log:
    def __init__(self):
        self.__id = None
        self.__date_time = None
        self.__description = None

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, new_id):
        self.__id = new_id
        return self.__id

    @property
    def date_time(self):
        return self.__date_time

    @date_time.setter
    def date_time(self, new_date_time):
        self.__date_time = new_date_time
        return self.__date_time

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, new_description):
        self.__description = new_description
        return self.__description
