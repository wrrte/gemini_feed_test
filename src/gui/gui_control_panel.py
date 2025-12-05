import tkinter as tk
from typing import Optional
from core.system import system

try:
    from device.device_control_panel_abstract import DeviceControlPanelAbstract
except ImportError:
    from ..device.device_control_panel_abstract import DeviceControlPanelAbstract


class GUIControlPanel(DeviceControlPanelAbstract):
    def __init__(self, master: Optional[tk.Tk] = None) -> None:
        super().__init__(master=master)
        self.state = "OFF"
        self.temp_new_pw = ""
        self.button_sequence = ""

        self.set_display_short_message1("System Off")
        self.set_display_short_message2("Press 1 to Turn On")
        self.set_powered_led(False)
        self.set_armed_led(False)

    def set_all_off(self) -> None:
        system.turn_off()
        self.state = "OFF"
        self.button_sequence = ""
        self.set_powered_led(False)
        self.set_armed_led(False)
        self.set_display_away(False)
        self.set_display_stay(False)

    def button(self, digit: str = "") -> None:
        if self.state == "OFF":
            if digit != "1":
                return
            system.turn_on()
            self.state = "LOCKED"
            self.button_sequence = ""
            self.set_display_short_message1("System Ready")
            self.set_display_short_message2("Enter Code")
            self.set_powered_led(True)
            if system.current_security_manager.now_security_mode:
                current_mode_name = system.current_security_manager.security_modes[
                    system.current_security_manager.now_security_mode
                ].name
                if current_mode_name == "Home":
                    self.set_display_stay(True)
                    self.set_display_away(False)
                elif current_mode_name == "Away":
                    self.set_display_away(True)
                    self.set_display_stay(False)
            return

        if self.state == "LOGGED_IN":
            if digit == "2":
                self.set_all_off()
                self.set_display_short_message1("System Off")
                self.set_display_short_message2("Press 1 to Turn On")
            elif digit == "3":
                system.reset()
                self.set_all_off()
                self.set_display_short_message1("System Reset & Off")
                self.set_display_short_message2("Press 1 to Turn On")
            elif digit == "7":
                self.set_display_away(True)
                self.set_display_stay(False)
                system.current_security_manager.set_security_mode_name("Away")
            elif digit == "8":
                self.set_display_away(False)
                self.set_display_stay(True)
                system.current_security_manager.set_security_mode_name("Home")
            elif digit == "9":
                self.state = "CHANGE_PW_CURRENT"
                self.button_sequence = ""
                self.set_display_short_message1("Change Password")
                self.set_display_short_message2("Enter Current Password")
            else:
                return  # ignore other keys
            return

        self.button_sequence += digit
        self.set_display_short_message2(f"Code: {self.button_sequence}")

        if len(self.button_sequence) < 4:
            return

        if self.state == "LOCKED":
            (result, message) = system.login_manager.cp_log_in(
                self.button_sequence, "master"
            )

            if result:
                self.state = "LOGGED_IN"
                self.set_display_short_message1("System Armed")
                self.set_display_short_message2("Logged In")
                if system.current_security_manager.now_security_mode == 0:
                    self.set_display_stay(True)
                    self.set_display_away(False)
                elif system.current_security_manager.now_security_mode == 1:
                    self.set_display_away(True)
                    self.set_display_stay(False)
            else:
                self.set_display_short_message1("Login Failed")
                self.set_display_short_message2(message)

            self.button_sequence = ""
            return

        if self.state == "CHANGE_PW_CURRENT":
            (result, message) = system.login_manager.cp_log_in(
                self.button_sequence, "master"
            )
            if not result:
                self.set_display_short_message1(message)
                self.set_display_short_message2("Try Again")
                self.button_sequence = ""
                return

            # success → move to next state
            self.state = "CHANGE_PW_NEW"
            self.button_sequence = ""
            self.set_display_short_message1("Enter New Password")
            self.set_display_short_message2("")
            return

        # --------------------------------------------------------
        # STATE 3: CHANGE_PW_NEW → store new password
        # --------------------------------------------------------
        if self.state == "CHANGE_PW_NEW":
            self.temp_new_pw = self.button_sequence
            self.button_sequence = ""
            self.state = "CHANGE_PW_CONFIRM"
            self.set_display_short_message1("Re-enter New Password")
            self.set_display_short_message2("")
            return

        # --------------------------------------------------------
        # STATE 4: CHANGE_PW_CONFIRM → verify match
        # --------------------------------------------------------
        if self.state == "CHANGE_PW_CONFIRM":
            if self.button_sequence != self.temp_new_pw:
                self.set_display_short_message1("Password Mismatch")
                self.set_display_short_message2("Enter New Password")
                self.state = "CHANGE_PW_NEW"  # or LOCKED, your choice
                self.button_sequence = ""
                self.temp_new_pw = ""
                return

            # SUCCESS
            system.login_manager.cp_change_password(self.temp_new_pw, "master")
            self.set_display_short_message1("Password Changed")
            self.set_display_short_message2("Successfully")

            # reset state machine
            self.state = "LOGGED_IN"
            self.button_sequence = ""
            self.temp_new_pw = ""
            return

    def button1(self) -> None:
        self.button("1")

    def button2(self) -> None:
        self.button("2")

    def button3(self) -> None:
        self.button("3")

    def button4(self) -> None:
        self.button("4")

    def button5(self) -> None:
        self.button("5")

    def button6(self) -> None:
        self.button("6")

    def button7(self) -> None:
        self.button("7")

    def button8(self) -> None:
        self.button("8")

    def button9(self) -> None:
        self.button("9")

    def button_star(self) -> None:
        if self.state != "OFF":
            self.set_armed_led(True)
            self.set_display_short_message1("PANIC ALARM!")
            self.set_display_short_message2("Help on the way")
            system.make_panic_phone_call()

    def button0(self) -> None:
        self.button("0")

    def button_sharp(self) -> None:
        if self.state != "OFF":
            self.set_armed_led(True)
            self.set_display_short_message1("PANIC ALARM!")
            self.set_display_short_message2("Help on the way")
            system.make_panic_phone_call()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = GUIControlPanel()
    app.mainloop()
