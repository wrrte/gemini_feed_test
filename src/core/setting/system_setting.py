class SystemSettings:
    def __init__(self):
        self.__system_lock_time = "300"
        self.__panic_phone_number = "112"
        self.__alarm_time_before_phonecall = "5"
        self.__home_phone_number = "01012345678"

    @property
    def system_lock_time(self):
        return self.__system_lock_time

    @system_lock_time.setter
    def system_lock_time(self, new_system_lock_time):
        self.__system_lock_time = new_system_lock_time
        return self.__system_lock_time

    @property
    def panic_phone_number(self):
        return self.__panic_phone_number

    @panic_phone_number.setter
    def panic_phone_number(self, new_panic_phone_number):
        self.__panic_phone_number = new_panic_phone_number
        return self.__panic_phone_number

    @property
    def alarm_time_before_phonecall(self):
        return self.__alarm_time_before_phonecall

    @alarm_time_before_phonecall.setter
    def alarm_time_before_phonecall(self, new_alarm_time_before_phonecall):
        self.__alarm_time_before_phonecall = new_alarm_time_before_phonecall
        return self.__alarm_time_before_phonecall

    @property
    def home_phone_number(self):
        return self.__home_phone_number

    @home_phone_number.setter
    def home_phone_number(self, new_home_phone_number):
        self.__home_phone_number = new_home_phone_number
        return self.__home_phone_number
