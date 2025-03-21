import ttkbootstrap as ttkb
from tkinter import Tk
from app.gui.emulator_view import EmulatorView
from app.gui.user_view import UserView


class MainWindow:
    def __init__(self, master, db_service):
        self.master = master
        self.master.title("RL Farm")
        self.style = ttkb.Style("darkly")  # Apply modern theme
        self.db_service = db_service  # ✅ Store the database service

        # ✅ Initialize UI Sections
        self.emulator_view = EmulatorView(self.master,self.db_service)
        self.user_view = UserView(self.master, self.db_service)

        # ✅ Configure Grid Layout
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

if __name__ == "__main__":
    root = Tk()
    app = MainWindow(root)
    root.mainloop()
