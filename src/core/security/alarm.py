class Alarm:
    def __init__(self):
        self.s: bool = False

    def siren(self):
        print("siren")
        print("\a")
        self.s = True

    def get(self) -> bool:
        if self.s:
            self.s = False
            return True
        return False
