"""
Main GUI
==============
Usage:
    python -m gui.gui_main
    (run from the "src" folder)
"""
import tkinter as tk
from typing import Type

from gui.gui_cameraview import CameraViewPage
from gui.gui_configuration import ConfigureSystemPage
from gui.gui_intrusionlog import ViewLogPage
from gui.gui_login_page import LoginPage
from gui.gui_securitymode import SecurityModePage
from gui.gui_securityzone import SecurityZonePage
from gui.gui_surveillance import FloorPlanPage
from gui.gui_thumbnails import ThumbnailsPage

from core.system import system

class GUIMain(tk.Toplevel):
    def __init__(self, master=None) -> None:
        tk.Toplevel.__init__(self, master)
        self.geometry("800x400")
        self.title("SafeHome")
        self.resizable(False, False)

        self.main_page_class = MainPage

        self.build_menubar()

        # creating a frame and assigning it to container
        container = tk.Frame(self, height=400, width=600)
        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames themselves later but let's add the components to the dictionary.
        for F in (LoginPage, MainPage, FloorPlanPage, SecurityModePage, SecurityZonePage, ThumbnailsPage,
                  CameraViewPage, ViewLogPage, ConfigureSystemPage, IdentityConfirmPage):
            frame = F(container, self)
            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def back_to_login(self) -> None:
        self.config(menu="")
        self.show_frame(LoginPage)

    def build_menubar(self) -> None:
        self.menubar = tk.Menu(self)

        nav_menu = tk.Menu(self.menubar, tearoff=0)
        nav_menu.add_command(label="Home", command=lambda: self.show_frame(MainPage))
        nav_menu.add_command(label="Configuration", command=lambda: self.secure_show_frame(ConfigureSystemPage))
        nav_menu.add_separator()
        nav_menu.add_command(label="Logout", command=self.logout)
        self.menubar.add_cascade(label="Navigate", menu=nav_menu)

        surv_menu = tk.Menu(self.menubar, tearoff=0)
        surv_menu.add_command(label="Thumbnail View", command=lambda: self.show_frame(ThumbnailsPage))
        surv_menu.add_command(label="Floor Plan View", command=lambda: self.show_frame(FloorPlanPage))
        self.menubar.add_cascade(label="Surveillance", menu=surv_menu)

        security_menu = tk.Menu(self.menubar, tearoff=0)
        security_menu.add_command(label="Security Modes", command=lambda: self.secure_show_frame(SecurityModePage))
        security_menu.add_command(label="Security Zones", command=lambda: self.secure_show_frame(SecurityZonePage))
        security_menu.add_command(label="Intrusion Log", command=lambda: self.secure_show_frame(ViewLogPage))
        self.menubar.add_cascade(label="Security", menu=security_menu)

    def show_frame(self, cont: Type[tk.Frame]) -> None:
        old_frame = self.frames[cont]
        old_frame.destroy()

        # recreate the frame
        container = old_frame.master
        new_frame = cont(container, self)

        # store it back
        self.frames[cont] = new_frame

        new_frame.grid(row=0, column=0, sticky="nsew")
        new_frame.tkraise()

    def open_camera_view(self, cam_id: int) -> None:
        camera_page = self.frames[CameraViewPage]
        camera_page.load_camera(cam_id)
        camera_page.tkraise()

    def logout(self) -> None:
        system.login_manager.web_log_out("WEB_BROWSER")
        self.config(menu="")
        self.show_frame(LoginPage)
    
    def secure_show_frame(self, target_frame):
        confirm_page = self.frames[IdentityConfirmPage]
        confirm_page.destroy()
        container = confirm_page.master
        new_frame = IdentityConfirmPage(container, self)
        self.frames[IdentityConfirmPage] = new_frame
        new_frame.grid(row=0, column=0, sticky="nsew")
        new_frame.set_target(target_frame)
        new_frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: GUIMain) -> None:
        tk.Frame.__init__(self, parent)

        # Container for centered layout
        center_frame = tk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            center_frame,
            text="SAFEHOME",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))

        def add_button(text, command):
            tk.Button(center_frame, text=text, width=30, command=command).pack(pady=5)
        add_button("Surveillance – Floor Plan View",
                   lambda: controller.show_frame(FloorPlanPage))
        add_button("Surveillance – Thumbnail View",
                   lambda: controller.show_frame(ThumbnailsPage))
        add_button("Security Modes",
                   lambda: controller.secure_show_frame(SecurityModePage))
        add_button("Security Zones",
                   lambda: controller.secure_show_frame(SecurityZonePage))
        add_button("Intrusion Log",
                   lambda: controller.secure_show_frame(ViewLogPage))
        add_button("Configuration",
                   lambda: controller.secure_show_frame(ConfigureSystemPage))
        add_button("Logout", controller.logout)


class IdentityConfirmPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: 'GUIMain') -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.REQUIRED_NUMBER = system.current_system_settings_manager.get_system_settings().home_phone_number
        tk.Label(self, text="Re-enter phone number", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self, text="For identity verification").pack(pady=5)

        vcmd = (self.register(self.validate_input), "%P")

        self.entry = tk.Entry(self, width=20, validate="key", validatecommand=vcmd)
        self.entry.pack(pady=10)

        self.error = tk.Label(self, text="", fg="red")
        self.error.pack()

        tk.Button(self, text="Confirm", command=self.check_number).pack(pady=15)

        tk.Button(self, text="Cancel",
                  command=lambda: controller.show_frame(MainPage)).pack()

        self.target_frame = None

    def validate_input(self, new_value):
        if new_value == "":
            return True  # allow clearing the field
        return new_value.isdigit() and len(new_value) <= 11

    def check_number(self):
        if self.entry.get() == self.REQUIRED_NUMBER:
            self.error.config(text="")
            if self.target_frame:
                self.controller.show_frame(self.target_frame)
        else:
            self.error.config(text="Incorrect phone number.")

    def set_target(self, frame_class):
        self.target_frame = frame_class
        self.entry.delete(0, tk.END)
        self.error.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = GUIMain(master=root)
    app.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
