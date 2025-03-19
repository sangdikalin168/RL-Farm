from app.gui.main_window import MainWindow
from app.services.mysql_service import MySQLService
import ttkbootstrap as ttkb
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding="utf-8")

def center_window(window, width=450, height=800):
    """Center the application window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_position = (screen_width // 2) - (width // 2)
    y_position = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x_position}+{y_position}")

if __name__ == "__main__":
    # ✅ Load environment variables
    load_dotenv()

    # ✅ Initialize MySQLService using .env (No hardcoded credentials)
    db_service = MySQLService()

    # ✅ Use ttkbootstrap's `Window` (Better UI theme support)
    app = ttkb.Window(themename="darkly")
    app.title("RL Farm")
    app.geometry("400x400")
    app.resizable(True, True)

    center_window(app)  # ✅ Center the window

    # ✅ Initialize main GUI with database service
    MainWindow(app, db_service)

    app.mainloop()  # ✅ Start GUI loop
