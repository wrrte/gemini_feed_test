import tkinter as tk
from typing import Any
from core.system import system


class LoginPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(
            self,
            text="LOGIN SAFEHOME SYSTEM",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # --- Username / Password Frame ---
        form_frame = tk.Frame(self)
        form_frame.pack(pady=20)

        tk.Label(form_frame, text='USERNAME', width=10, anchor='w').grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form_frame, text='PASSWORD', width=10, anchor='w').grid(row=1, column=0, padx=5, pady=5)

        # --- Validation for character limit ---
        def on_validate(P: str) -> bool:
            return len(P) <= 10  # limit to 10 characters

        vcmd = (self.register(on_validate), '%P')

        self.username_entry = tk.Entry(form_frame, width=15, validate='key', validatecommand=vcmd)
        self.password_entry = tk.Entry(form_frame, width=15, validate='key', validatecommand=vcmd, show='*')

        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # --- Login Button aligned with entries ---
        login_button = tk.Button(
            form_frame,
            text="LOGIN",
            width=15,              # Same width as entry boxes
            command=self.login
        )
        login_button.grid(row=2, column=1, padx=5, pady=(10, 0))

        # --- Error label ---
        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack(pady=5)

    def login(self) -> None:
        username = self.username_entry.get()
        password = self.password_entry.get()

        (result, message) = system.login_manager.web_log_in(username, password, "WEB_BROWSER")

        if result:
            self.error_label.config(text="")
            self.controller.config(menu=self.controller.menubar)
            self.controller.show_frame(self.controller.main_page_class)
        else:
            self.error_label.config(text=message)
