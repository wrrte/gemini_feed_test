# main.py
# import core.system for the first time to init the system
from core.system import system
from gui.gui_control_panel import GUIControlPanel
from gui.gui_main import GUIMain
from gui.gui_sensorintruder import GUISensorIntruder
import tkinter as tk

def main():
    root = tk.Tk()
    root.withdraw()

    app = GUIMain(master=root)
    app.withdraw()
    sensor_test_gui = GUISensorIntruder(master=root)

    control_panel = GUIControlPanel(master=root)

    app.protocol("WM_DELETE_WINDOW", root.quit)
    sensor_test_gui.protocol("WM_DELETE_WINDOW", root.quit)
    control_panel.protocol("WM_DELETE_WINDOW", root.quit)

    system.current_control_panel = control_panel
    system.current_app = app
    root.mainloop()


if __name__ == "__main__":
    main()
