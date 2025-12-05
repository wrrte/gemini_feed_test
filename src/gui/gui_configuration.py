import tkinter as tk
from typing import Any
from core.system import system


class ConfigureSystemPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(parent)
        self.controller = controller

        tk.Label(
            self,
            text="SAFEHOME CONFIGURATION",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        def make_validator(max_len):
            def validate(P):
                # Allow empty (so backspace works)
                if P == "":
                    return True
                # Must be digits AND within length
                return P.isdigit() and len(P) <= max_len
            return validate

        # ============================================================
        # LEFT COLUMN — SYSTEM SETTINGS
        # ============================================================
        left = tk.LabelFrame(main_frame, text="System Settings",
                             font=("Arial", 12, "bold"), padx=15, pady=15)
        left.pack(side="left", fill="both", expand=True, padx=10)

        # --- Create fields dynamically ---
        self.fields = {}

        def add_field(parent, label_text, var_name, max_len):
            row_frame = tk.Frame(parent)
            row_frame.pack(fill="x", pady=5)

            tk.Label(row_frame, text=label_text, width=25, anchor="w").pack(side="left")
            vcmd = (self.register(make_validator(max_len)), "%P")
            entry = tk.Entry(row_frame, width=15,
                             validate="key", validatecommand=vcmd)
            entry.pack(side="right")
            self.fields[var_name] = entry

        add_field(left, "System Lock Time (s):", "system_lock_time", 3)
        add_field(left, "Panic Phone Number:", "panic_phone_number", 11)
        add_field(left, "Alarm Time Before Phonecall (s):", "alarm_time_before_phonecall", 3)
        add_field(left, "Home Phone Number:", "home_phone_number", 11)

        # Pre-fill from SystemSettings if available
        self.settings = system.current_system_settings_manager.get_system_settings()
        if self.settings:
            self.fields["system_lock_time"].insert(0, self.settings.system_lock_time or "ERROR")
            self.fields["panic_phone_number"].insert(0, self.settings.panic_phone_number or "ERROR")
            self.fields["alarm_time_before_phonecall"].insert(0, self.settings.alarm_time_before_phonecall or "ERROR")
            self.fields["home_phone_number"].insert(0, self.settings.home_phone_number or "ERROR")

        # ============================================================
        # RIGHT COLUMN — PASSWORD SETTINGS
        # ============================================================
        right = tk.LabelFrame(main_frame, text="Password Settings",
                              font=("Arial", 12, "bold"), padx=15, pady=15)
        right.pack(side="right", fill="both", expand=True, padx=10)

        self.password_fields = {}

        def add_pw_field(parent, label_text, var_name, max_len):
            row_frame = tk.Frame(parent)
            row_frame.pack(fill="x", pady=5)

            tk.Label(row_frame, text=label_text, width=25, anchor="w").pack(side="left")
            vcmd = (self.register(make_validator(max_len)), "%P")
            entry = tk.Entry(row_frame, width=15,
                             show="*", validate="key", validatecommand=vcmd)
            entry.pack(side="right")
            self.password_fields[var_name] = entry

        add_pw_field(right, "Web Password:", "web_pw", 11)
        add_pw_field(right, "Confirm Web Password:", "web_pw_confirm", 11)
        add_pw_field(right, "Control Panel Password:", "master_pw", 4)
        add_pw_field(right, "Confirm Control Panel Password:", "master_pw_confirm", 4)

        self.response_label = tk.Label(self, text="", fg="red", font=("Arial", 10))
        self.response_label.pack(pady=5)
        
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="SAVE", width=15,
                  command=self.save_settings).pack(side="left", padx=10)

        tk.Button(button_frame, text="CANCEL", width=15,
                  command=lambda: controller.show_frame(controller.main_page_class)
                  ).pack(side="right", padx=10)

    def save_settings(self) -> None:
        """Validate and save system + password settings."""
        errors = []
        
        # --- Validate passwords ---
        def check_pw(name):
            pw = self.password_fields[f"{name}_pw"].get()
            confirm = self.password_fields[f"{name}_pw_confirm"].get()

            if pw == "" and confirm == "":
                return None
            
            if pw == "" or confirm == "":
                errors.append(f"{name.capitalize()} password does not match")
                return None

            if pw != confirm:
                errors.append(f"{name.capitalize()} password does not match")

            if name == "master":
                if pw is not None and len(pw) != 4:
                    errors.append("Control panel password must be exactly 4 digits")
                    return None
            
            return pw

        web_pw = check_pw("web")
        master_pw = check_pw("master")
        
        for var_name, entry in self.fields.items():
            if entry.get().strip() == "":
                errors.append(f"{var_name.replace('_', ' ').capitalize()} cannot be empty")

        if errors:
            self.response_label.config(text="\n".join(errors), fg="red")
            return

        # --- Save system settings ---
        self.settings.system_lock_time = self.fields["system_lock_time"].get()
        self.settings.panic_phone_number = self.fields["panic_phone_number"].get()
        self.settings.alarm_time_before_phonecall = self.fields["alarm_time_before_phonecall"].get()
        self.settings.home_phone_number = self.fields["home_phone_number"].get()

        system.current_system_settings_manager.update_system_settings(self.settings)
        
        if web_pw is not None:
            system.login_manager.web_change_password("WEB_BROWSER", web_pw)
        if master_pw is not None:
            system.login_manager.cp_change_password(master_pw, "master")

        self.response_label.config(text="Settings saved successfully!", fg="green")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = ConfigureSystemPage(root, root)
    page.pack()
    root.mainloop()
