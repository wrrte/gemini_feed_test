import tkinter as tk
from tkinter import ttk
from typing import Any
from core.system import system


class ViewLogPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(parent)
        self.controller = controller

        tk.Label(
            self,
            text="INTRUSION LOGS",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # ============================================================
        # FRAME WITH SCROLLABLE LOG LIST
        # ============================================================
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # Canvas + Scrollbar
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # This frame will hold the log rows
        self.log_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.log_frame, anchor="nw")

        # Configure canvas resizing
        self.log_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ============================================================
        # TABLE HEADER
        # ============================================================
        header = tk.Frame(self.log_frame)
        header.pack(fill="x", pady=(0, 5))

        tk.Label(header, text="ID", width=10, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(header, text="DATE/TIME", width=25, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=1,
                                                                                                  padx=5)
        tk.Label(header, text="DESCRIPTION", width=60, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=2,
                                                                                                    padx=5)

        ttk.Separator(self.log_frame, orient="horizontal").pack(fill="x", pady=5)

        # Actual log rows container
        self.rows_container = tk.Frame(self.log_frame)
        self.rows_container.pack(fill="x")

        # Load logs now
        self.load_logs()

        # ============================================================
        # BACK BUTTON
        # ============================================================
        tk.Button(
            self,
            text="← Back",
            width=12,
            command=lambda: controller.show_frame(controller.main_page_class)
        ).pack(pady=10)

    # ============================================================
    # Load logs into GUI
    # ============================================================
    def load_logs(self) -> None:
        """Loads log entries into the page."""
        # Remove old rows if the page is refreshed
        for widget in self.rows_container.winfo_children():
            widget.destroy()

        logs = system.current_log_manager.get_log_list()

        for log in logs:
            row = tk.Frame(self.rows_container)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=str(log.id), width=10, anchor="w").grid(row=0, column=0, padx=5)
            tk.Label(row, text=str(log.date_time), width=25, anchor="w").grid(row=0, column=1, padx=5)
            tk.Label(row, text=str(log.description), width=60, anchor="w").grid(row=0, column=2, padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = ViewLogPage(root, root)
    page.pack()
    root.mainloop()
