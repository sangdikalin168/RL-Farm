#emulator_view
import json
import random
import shutil
import string
import time
import pyotp
import ttkbootstrap as ttkb
from ttkbootstrap import Button
from tkinter import messagebox
from app.controllers.adb_controller import ADBController
from app.controllers.emulator_controller import MuMuPlayerController
from concurrent.futures import ThreadPoolExecutor
import threading
import ttkbootstrap as ttkb
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
from app.services.mysql_service import MySQLService
from app.controllers.emulator_controller import MuMuPlayerController
from concurrent.futures import ThreadPoolExecutor
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from app.utils.email_service import get_domain_confirm_code, get_domain_confirm_email
from app.utils.five_sim import FiveSimAPI
from app.utils.five_sim_generate import five_sim_generate_info
from app.utils.gmail_api import get_order, get_otp
from app.utils.user_generator import generate_info
from app.utils.vietnam_api import get_otp_stp, rent_gmail
from app.utils.zoho import get_confirmation_code
from app.utils.zoho_api import zoho_api_get_confirmation_code, zoho_api_get_security_code
from app.utils.zoho_generate import generate_zoho_info


from dataclasses import dataclass
@dataclass
class EmailCredentials:
    email: str
    pass_mail: str

class EmulatorView:
    def __init__(self, master, db_service):
        self.master = master
        self.db_service = db_service
        self.emulator = MuMuPlayerController(self)  # ✅ Pass `self` (MainWindow) as a reference to EmulatorController
        self.selected_emulators = {}
        self.selected_package = tk.StringVar(value="com.facebook.katana")
        self.selected_mail = tk.StringVar(value="zoho")
        self.selected_reg_type = tk.StringVar(value="full")  
        self.two_factor_checked = tk.StringVar(value="false")  # Default to "false" (No 2FA)
        self.reg_gmail = False

        
        self.email_password_mapping = {
            "eth168@zohomail.com": "SeJrd7FY5d2s",
            "bnb168@zohomail.com": "ThCQMwH903Pf",
            "avax168@zohomail.com": "ydaUqLHEgsvE",
        }
        self.selected_fivesim_email = tk.StringVar(value=list(self.email_password_mapping.keys())[0])
        
        self.api_mapping = {
            "API 1": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzUzMDgxMjgsImlhdCI6MTc0Mzc3MjEyOCwicmF5IjoiN2YyMTMyMjNmNTcxMjIwMTUzMjM2NDhhM2JiYjM1ZjciLCJzdWIiOjMxMzM0ODR9.aHYVLcrpXSBva917hFbtXAqMgppHuJ5c1yYRzqwEl7QAg8dgehZR7DaWqbbnGhRUThUZqpv6P6NwEDfNa9v2vxFJelwM-XMANchSqOd8vrSht-n1Z_6aLEWefwCYvRHbjT4z3lTB4kJ7X4hkVELiy03PjYvuhCdUGQeV_L0L53LRgrJ2aLi71mv6TZ7MKy7BfYzXmFMaiZ0azH5qbb6jaQR_REPR_1AD0gf4E5-Ue9DP66FunR1UIxtVImZV7Htd0YswQYoJe8-cOrbTlWRMbEoiGfsLjFm17TMj6Ol_tYsdl4d_L6NFWG2mrdd58xGMAM1nnwldzOalkYn1CRRPOg",
            "API 2": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzUzMDE1MDcsImlhdCI6MTc0Mzc2NTUwNywicmF5IjoiODA3NjMzZGNmMjY4OGMxODFiNDJkMDdlZTM3ZDI5ZTgiLCJzdWIiOjMxMjk2OTh9.hTmcHi0_g7xcoI9Hfe9NQfzIeGxBNHn9Zgk2uQSq-QUAhQF4mhKUujjBqpgp8XR5aCaiAoXu0JpkD1UNtAi3SiA6LxJbFe1iH-DFyDylje7pAZ3LcgzYQo1jGWz8bEXE9Hzb8MLpJW6MsjNjYlGti2NwiR3r3Yo3MAcVVmMpbrlptM7rgA8fuIYND2zpdfx8gIWlII-ERnFGbaX6ycM23321XUnebf3P3MzImTAJYgY5Cx_IUxyU57nBhTOAbSrZTssK0b4uBEeo29nyKVN-2li5kCDvhDJpoSkUlJGWOb6rYayPWiDeZBMdglK6v0nSttrZRETKVRfp6zbRslTTFQ",
            "API 3": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzI0NjEwNTMsImlhdCI6MTc0MDkyNTA1MywicmF5IjoiNjFhZTM4NTQ3NmY3OGM0MzlkODk1ZGY2YTkyMTg4NDEiLCJzdWIiOjIwNTQ3OTF9.hBcz9PwIMtnn60JM_dQ5p-glZ_lFb8j3XH0oq8Hkp4QcSo8oT9ezngA-KgwIFn_c-rRoKM81MQOvdIuN7-cdPhUQhsCi3GgiXS2fF1i03GU8qCR61E2rTkDFKNy-Da0g0-T5fPE_bGIqltce_3a-uLXKx5HHiLN1oUgHdX3v0In2ghIsBKIILJDYGwGVppjly3eaitzwpDfBRrkOJoPeEoce22V9FhgFXrn7JXeTugb_G7FLgS7PFecFwt45Cy2Q408PBD81GknqdlcfTNES2K9D6dMoSFykvqC65WEF6Exp3NFM1PBe9N1n0ezoSYzYCGYM_GBk2Uwpvxr2GajJCA",
        }
        
        self.country_operator_mapping = {
            "england": ["virtual38", "virtual51", "virtual52", "virtual60","virtual61"],
            "mongolia": ["virtual21"],
            "cambodia": ["virtual49"],
        }
        

        # ✅ Setup Emulator UI
        self.setup_emulator_ui()

    def setup_emulator_ui(self):
        """Setup the Emulator UI Components""" 
        
        ICON_SIZE = (25, 25)  # Define constant for image resizing

        # Create main frame
        main_frame = ttkb.Frame(self.master, padding=5)
        main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=0)  # Buttons rows
        main_frame.grid_rowconfigure(1, weight=0)  # Buttons rows
        main_frame.grid_rowconfigure(2, weight=0)  # Buttons rows
        main_frame.grid_rowconfigure(3, weight=0)  # Buttons rows
        
        
        # Row 0: First set of buttons
        button_frame_1 = ttkb.Frame(main_frame, padding=5)
        button_frame_1.grid(row=0, column=0, sticky="ew")
        
        
        # Row 1: Second set of buttons
        button_frame_2 = ttkb.Frame(main_frame, padding=5)
        button_frame_2.grid(row=1, column=0, sticky="ew")


        # Row 2: Third set of buttons
        button_frame_3 = ttkb.Frame(main_frame, padding=5)
        button_frame_3.grid(row=2, column=0, sticky="ew")
        
        # Row 3: Fourth set of buttons
        button_frame_4 = ttkb.Frame(main_frame, padding=5)
        button_frame_4.grid(row=3, column=0, sticky="ew")
        
        
        # Row 4: Fifth set of buttons
        button_frame_5 = ttkb.Frame(main_frame, padding=5)
        button_frame_5.grid(row=4, column=0, sticky="ew")
        
        # ✅ Frame for Emulator List with Border
        emulator_frame = ttkb.Labelframe(main_frame, text="Emulator List", padding=5)
        emulator_frame.grid(row=5, column=0, columnspan=6, pady=(5, 0), sticky="nsew")
        # ✅ Configure grid weights for emulator_frame
        emulator_frame.grid_rowconfigure(0, weight=0)  # Header row
        emulator_frame.grid_rowconfigure(1, weight=1)  # TreeView row
        emulator_frame.grid_columnconfigure(0, weight=1)  # TreeView column
        emulator_frame.grid_columnconfigure(1, weight=0)  # Scrollbar column
        emulator_frame.grid_columnconfigure(2, weight=0)  # Scrollbar column
        emulator_frame.grid_columnconfigure(3, weight=0)  # Scrollbar column
        emulator_frame.grid_columnconfigure(4, weight=0)  # Scrollbar column
        emulator_frame.grid_columnconfigure(5, weight=0)  # Scrollbar column
                

        def resource_path(relative_path):
            try:
                # PyInstaller stores temp files here
                base_path = sys._MEIPASS
            except AttributeError:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        # ✅ Function to Load Icons
        def load_icon(filename):
            try:
                path = resource_path(os.path.join("assets", filename))
                return ImageTk.PhotoImage(Image.open(path).resize(ICON_SIZE, Image.Resampling.LANCZOS))
            except FileNotFoundError:
                print(f"Warning: {filename} not found.")
                return None

        # ✅ Load Icons
        self.start_photo = load_icon("start_icon.png")
        self.stop_photo = load_icon("stop_icon.png")
        self.sort_photo = load_icon("sort_icon.png")

        # ✅ Start & Stop Buttons
        if self.start_photo:
            start_button = ttkb.Button(button_frame_1, image=self.start_photo, command=self.start_selected_players, style="success.Compact.TButton", width=20, padding=2)
            start_button.grid(row=0, column=0, padx=5)

        if self.stop_photo:
            stop_button = ttkb.Button(button_frame_1, image=self.stop_photo, command=self.stop_selected_players, style="danger.Compact.TButton", width=20, padding=2)
            stop_button.grid(row=0, column=1, padx=5)

        if self.sort_photo:
            sort_button = ttkb.Button(button_frame_1, image=self.sort_photo, command=self.sort_emulators, style="info.Compact.TButton", width=20, padding=2)
            sort_button.grid(row=0, column=2, padx=5)

        # ✅ Start Register Button (Moved to the same row as Change IMEI)
        self.start_register_button = ttkb.Button(button_frame_1, text="Start Register", command=self.start_register_action, style="success.TButton")
        self.start_register_button.grid(row=0, column=3, padx=5)

        self.change_imei_button = ttkb.Button(button_frame_1, text="Change IMEI", command=self.emulator.change_imei, style="success.TButton")
        self.change_imei_button.grid(row=0, column=5, padx=5)
        
        self.reg_gmail_button = ttkb.Button(button_frame_1, text="Reg Gmail", command=self.start_register_gmail, style="success.TButton")
        self.reg_gmail_button.grid(row=0, column=6, padx=5)
    

        # ✅ Frame for Mode Selection Checkboxes with Border
        register_frame = ttkb.Labelframe(button_frame_2, text="FB Selection", padding=5)
        register_frame.grid(row=0, column=0, columnspan=6, pady=(5, 0), sticky="w")

        # ✅ Lite Checkbox
        self.lite_checkbox = ttkb.Radiobutton(register_frame, text="Lite", variable=self.selected_package, value="com.facebook.lite", style="primary.TRadiobutton")
        self.lite_checkbox.grid(row=0, column=0, sticky="w", padx=5)

        # ✅ Katana Checkbox
        self.katana_checkbox = ttkb.Radiobutton(register_frame, text="Katana", variable=self.selected_package, value="com.facebook.katana", style="primary.TRadiobutton")
        self.katana_checkbox.grid(row=0, column=1, sticky="w", padx=5)
        
        self.chrome_checkbox = ttkb.Radiobutton(register_frame, text="Chrome", variable=self.selected_package, value="chrome", style="primary.TRadiobutton")
        self.chrome_checkbox.grid(row=0, column=2, sticky="w", padx=5)
        
        
        # ✅ Frame for Mail Selection Checkboxes with Border
        mode_selection_frame = ttkb.Labelframe(button_frame_3, text="Mail Selection", padding=5)
        mode_selection_frame.grid(row=2, column=0, columnspan=6, pady=(5, 0), sticky="w")

        self.zoho_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Zoho", variable=self.selected_mail, value="zoho", style="primary.TRadiobutton")
        self.zoho_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        
        self.yandex_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Yandex", variable=self.selected_mail, value="yandex", style="primary.TRadiobutton")
        self.yandex_checkbox.grid(row=0, column=1, sticky="w", padx=5)
        
        self.customer_email_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Domain", variable=self.selected_mail, value="custom", style="primary.TRadiobutton")
        self.customer_email_checkbox.grid(row=0, column=2, sticky="w", padx=5)

        self.five_sim_checkbox = ttkb.Radiobutton(mode_selection_frame, text="5SIM", variable=self.selected_mail, value="five_sim", style="primary.TRadiobutton")
        self.five_sim_checkbox.grid(row=0, column=3, sticky="w", padx=5)
        
        self.gmail_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Gmail Loop", variable=self.selected_mail, value="gmail", style="primary.TRadiobutton")
        self.gmail_checkbox.grid(row=0, column=4, sticky="w", padx=5)

        # --- 5SIM Cascading Selections ---
        # Create a frame for the extra 5SIM options; initially hidden
        self.fivesim_options_frame = ttkb.Frame(mode_selection_frame)
        self.fivesim_options_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        self.fivesim_options_frame.grid_remove()  # Hide by default

        # Create a dropdown (combobox) for selecting an email from our mapping.
        ttkb.Label(self.fivesim_options_frame, text="Email:").grid(row=0, column=0, sticky="w")
        self.fivesim_email_combobox = ttkb.Combobox(
            self.fivesim_options_frame,
            textvariable=self.selected_fivesim_email,
            state="readonly",
            values=list(self.email_password_mapping.keys())
        )
        self.fivesim_email_combobox.grid(row=0, column=1, sticky="w", padx=5)

        # API Selection
        self.selected_api = tk.StringVar(value="API 1")
        ttkb.Label(self.fivesim_options_frame, text="API:").grid(row=0, column=2, sticky="w")
        self.fivesim_api_combobox = ttkb.Combobox(
            self.fivesim_options_frame,
            textvariable=self.selected_api,
            state="readonly",
            values=list(self.api_mapping.keys())
        )
        self.fivesim_api_combobox.grid(row=0, column=3, sticky="w", padx=5)


        # --- Operator Selection ---
        ttkb.Label(self.fivesim_options_frame, text="Operator:").grid(row=1, column=2, sticky="w")
        # Create a StringVar for the operator selection.
        self.selected_operator = tk.StringVar()
        self.fivesim_operator_combobox = ttkb.Combobox(
            self.fivesim_options_frame,
            textvariable=self.selected_operator,
            state="readonly",
            values=[]  # Initially empty; it will be populated based on the country.
        )
        self.fivesim_operator_combobox.grid(row=1, column=3, sticky="w", padx=5)
        

        # --- Country Selection ---
        ttkb.Label(self.fivesim_options_frame, text="Country:").grid(row=1, column=0, sticky="w")
        # Create a StringVar for the country selection and assign a default value.
        self.selected_country = tk.StringVar(value="england")
        self.fivesim_country_combobox = ttkb.Combobox(
            self.fivesim_options_frame,
            textvariable=self.selected_country,
            state="readonly",
            values=list(self.country_operator_mapping.keys())
        )
        self.fivesim_country_combobox.grid(row=1, column=1, sticky="w", padx=5)

        # Attach the trace to the country StringVar so that changes trigger the callback.
        self.selected_country.trace("w", self.country_selection_changed)
        
        # Call the callback right away to update the operator combobox with the default value.
        self.country_selection_changed()
        self.selected_mail.trace("w", self.mail_selection_changed)
        
        # ✅ Reg Novery Or Reg Full 2FA Or No 2FA 
        reg_type_frame = ttkb.Labelframe(button_frame_4, text="Reg Type", padding=5)
        reg_type_frame.grid(row=0, column=0, sticky="w")

        self.type_full_checkbox = ttkb.Radiobutton(reg_type_frame, text="Full", variable=self.selected_reg_type, value="full", style="primary.TRadiobutton")
        self.type_full_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        
        self.type_novery_checkbox = ttkb.Radiobutton(reg_type_frame, text="No Very", variable=self.selected_reg_type, value="novery", style="primary.TRadiobutton")
        self.type_novery_checkbox.grid(row=0, column=1, sticky="w", padx=5)
        
        self.type_gmail_checkbox = ttkb.Radiobutton(reg_type_frame, text="Wait At Mail", variable=self.selected_reg_type, value="wait_mail", style="primary.TRadiobutton")
        self.type_gmail_checkbox.grid(row=0, column=2, sticky="w", padx=5)
        
        
        
        # ✅ 2FA Or No 2FA 
        reg_two_factor_frame = ttkb.Labelframe(button_frame_4, text="2FA", padding=5)
        reg_two_factor_frame.grid(row=0, column=2,padx=(10,0), sticky="w")
        self.type_2fa_checkbox = ttkb.Radiobutton(reg_two_factor_frame, text="2FA", variable=self.two_factor_checked, value="true", style="primary.TRadiobutton")
        self.type_2fa_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        self.type_no_2fa_checkbox = ttkb.Radiobutton(reg_two_factor_frame, text="No 2FA", variable=self.two_factor_checked, value="false", style="primary.TRadiobutton")
        self.type_no_2fa_checkbox.grid(row=0, column=1, sticky="w", padx=5)
        
        
        # ✅ Select All Button
        self.select_all_button = ttkb.Button(button_frame_5, text="Select All", command=self.toggle_select_all, style="primary.TButton")
        self.select_all_button.grid(row=4, column=0, pady=5, sticky="nsew")


        # ✅ Dictionary to Store Checkbox States
        self.selected_emulators = {} 

        # ✅ Create Emulator TreeView
        self.emulator_tree = ttkb.Treeview(
            emulator_frame,
            columns=("Select", "No", "Device", "Status"),
            show="headings",
            height=15,
            selectmode="extended"  # Allows drag selection + Ctrl/Shift click
        )

        # ✅ Set Column Headings
        self.emulator_tree.heading("Select", text="✔", anchor="center")
        self.emulator_tree.heading("No", text="No", anchor="center")
        self.emulator_tree.heading("Device", text="Device", anchor="center")
        self.emulator_tree.heading("Status", text="Status", anchor="center")

        # ✅ Set Column Widths & Enable Resizing
        self.emulator_tree.column("Select", width=30, minwidth=30, stretch=False, anchor="center")
        self.emulator_tree.column("No", width=30, minwidth=30, stretch=False, anchor="center")
        self.emulator_tree.column("Device", width=70, minwidth=70, stretch=True, anchor="center")
        self.emulator_tree.column("Status", width=120, minwidth=120, stretch=True, anchor="center")

        # ✅ Place TreeView inside the grid
        self.emulator_tree.grid(row=1, column=0, columnspan=4, sticky="nsew")

        # ✅ Ensure Parent Frame Expands with the Window
        emulator_frame.grid_rowconfigure(1, weight=1)
        emulator_frame.grid_columnconfigure(0, weight=1)

        # ✅ Add Scrollbar to TreeView
        emulator_scrollbar = ttkb.Scrollbar(emulator_frame, orient="vertical", command=self.emulator_tree.yview)
        self.emulator_tree.configure(yscrollcommand=emulator_scrollbar.set)
        emulator_scrollbar.grid(row=1, column=4, sticky="ns")  # Adjusted to correct position

        # ✅ Load players on startup & Bind checkbox toggle function
        self.load_players()

        # Track drag state
        self.drag_state = {
            'start_item': None,
            'start_index': None,
            'last_index': None,
            'direction': None,  # 'up' or 'down'
            'initial_selection': None  # Store initial checkbox states
        }
        
        # Bind mouse events
        self.emulator_tree.bind("<Button-1>", self.on_mouse_click, add="+")
        self.emulator_tree.bind("<B1-Motion>", self.on_mouse_drag, add="+")
        self.emulator_tree.bind("<ButtonRelease-1>", self.on_mouse_release, add="+")

    def country_selection_changed(self, *args):
        selected_country = self.selected_country.get()
        operators = self.country_operator_mapping.get(selected_country, [])
        # Update the combobox values
        self.fivesim_operator_combobox['values'] = operators
        if operators:
            # Set the default value explicitly for both the StringVar and the widget
            self.selected_operator.set(operators[0])
            self.fivesim_operator_combobox.set(operators[0])
        else:
            self.selected_operator.set("")
            self.fivesim_operator_combobox.set("")

    def get_country(self) -> str:
        """
        Returns the selected country. (You can modify this if you have a separate country code mapping.)
        """
        return self.selected_country.get()

    def get_email_credentials(self) -> EmailCredentials:
        """
        Returns the selected email and its fixed password as an EmailCredentials object.
        """
        selected_email = self.fivesim_email_combobox.get()
        if not selected_email:
            messagebox.showerror("Input Error", "Please select an email for 5SIM.")
            return None
        fixed_pass = self.email_password_mapping.get(selected_email)
        return EmailCredentials(email=selected_email, pass_mail=fixed_pass)

    def get_operator(self) -> str:
        """
        Retrieves the selected operator from the combobox.
        """
        operator = self.fivesim_operator_combobox.get()
        if not operator:
            messagebox.showerror("Input Error", "Please select an operator for 5SIM.")
            return None
        return operator

    def get_api_key(self) -> str:
        """
        Retrieves the API key from the mapping based on the selected API option.
        """
        selected_api = self.fivesim_api_combobox.get()
        if not selected_api:
            messagebox.showerror("Input Error", "Please select an API option for 5SIM.")
            return None
        return self.api_mapping.get(selected_api)

    def mail_selection_changed(self, *args):
        """Show the cascading 5SIM dropdowns when 'five_sim' is selected, hide otherwise."""
        if self.selected_mail.get() == "five_sim":
            self.fivesim_options_frame.grid()  # Show the extra options
        else:
            self.fivesim_options_frame.grid_remove()  # Hide the extra options

    def load_players(self):
        """Fetch player list and update TreeView with optimized performance and JSON parsing."""
        try:
            # Clear existing data
            self.emulator_tree.delete(*self.emulator_tree.get_children())
            self.selected_emulators = {}

            # Get emulator data with progress feedback
            self._show_loading_progress()
            emulator_data = self.emulator.get_all_emulator_status()
            self._hide_loading_progress()

            if not emulator_data:
                self.emulator_tree.insert("", "end", values=("☐", "0", "No Players Found", "Not Running"))
                return

            # Process and sort players
            sorted_players = sorted(emulator_data.items(), key=lambda x: x[0])
            for idx, (player_index, data) in enumerate(sorted_players, start=1):
                status = data.get("status", "Unknown")
                
                # Parse device_id (handling both JSON and direct port cases)
                raw_device = data.get("device_id")
                device_display = "Not Available"
                
                if raw_device and "adb_port" in str(raw_device):
                    try:
                        if isinstance(raw_device, str):
                            port_info = json.loads(raw_device)
                        else:
                            port_info = raw_device
                        device_display = f"127.0.0.1:{port_info.get('adb_port', '?')}"
                    except (json.JSONDecodeError, AttributeError) as e:
                        print(f"⚠️ Error parsing device info for player {player_index}: {e}")
                        device_display = "Invalid Format"
                elif raw_device:
                    device_display = str(raw_device)

                # Insert into treeview with status-based coloring
                item_id = self.emulator_tree.insert(
                    "", "end", 
                    values=("☐", str(idx), device_display, status),
                    tags=(status.lower().replace(" ", "_"),)
                )
                self.selected_emulators[item_id] = False



        except Exception as e:
            self._hide_loading_progress()
            print(f"⛔ Error loading players: {e}")
            self.emulator_tree.insert("", "end", 
                values=("☐", "0", "Error Loading Data", "Error"),
                tags=("error",)
            )

    def _show_loading_progress(self):
        """Show loading progress indicator."""
        self.loading_window = ttkb.Toplevel(self.master)
        self.loading_window.title("Loading Emulators")
        self.loading_window.geometry("300x80")
        self.loading_window.resizable(False, False)
        
        ttkb.Label(self.loading_window, text="Scanning for emulators...").pack(pady=10)
        self.loading_progress = ttkb.Progressbar(
            self.loading_window, 
            orient="horizontal", 
            mode="indeterminate"
        )
        self.loading_progress.pack(fill="x", padx=20)
        self.loading_progress.start()

    def _hide_loading_progress(self):
        """Hide loading progress indicator."""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def on_mouse_click(self, event):
        """Handle mouse click events"""
        col = self.emulator_tree.identify_column(event.x)
        row = self.emulator_tree.identify_row(event.y)
        
        if row:  # If clicked on a row
            if col == "#1":  # Checkbox column
                # Toggle checkbox
                current_value = self.selected_emulators.get(row, False)
                self.selected_emulators[row] = not current_value
                self.update_checkbox_display()
                return "break"  # Prevent treeview selection
            else:
                # Initialize drag state
                self.drag_state = {
                    'start_item': row,
                    'start_index': self.emulator_tree.index(row),
                    'last_index': self.emulator_tree.index(row),
                    'direction': None,
                    'initial_selection': dict(self.selected_emulators)  # Save current state
                }
                return None
        
    def on_mouse_drag(self, event):
        """Handle mouse drag with directional selection"""
        row = self.emulator_tree.identify_row(event.y)
        
        if not row or not self.drag_state['start_item']:
            return
        
        current_index = self.emulator_tree.index(row)
        last_index = self.drag_state['last_index']
        
        # Skip if we're on the same row
        if current_index == last_index:
            return
        
        # Determine direction (first movement)
        if self.drag_state['direction'] is None:
            if current_index > last_index:
                self.drag_state['direction'] = 'down'
            else:
                self.drag_state['direction'] = 'up'
        
        # Update last index
        self.drag_state['last_index'] = current_index
        
        # Get range of items to process
        start_idx = self.drag_state['start_index']
        end_idx = current_index
        
        # Process each item in the range
        children = self.emulator_tree.get_children()
        for idx in range(min(start_idx, end_idx), max(start_idx, end_idx) + 1):
            item_id = children[idx]
            
            # Apply selection based on direction
            if self.drag_state['direction'] == 'down':
                self.selected_emulators[item_id] = True  # Select
            else:
                self.selected_emulators[item_id] = False  # Unselect
        
        self.update_checkbox_display()

    def on_mouse_release(self, event):
        """Handle mouse release and cleanup"""
        # Check if we had an active drag operation
        if self.drag_state['start_item']:
            # Optional: Add any final processing here
            pass
        
        # Reset drag state
        self.drag_state = {
            'start_item': None,
            'start_index': None,
            'last_index': None,
            'direction': None,
            'initial_selection': None
        }

    def update_checkbox_display(self):
        """Update the visual state of checkboxes and row backgrounds"""
        for item_id in self.emulator_tree.get_children():
            checked = self.selected_emulators.get(item_id, False)
            value = "☐"
            if checked:
                value = "✔"
            
            self.emulator_tree.set(item_id, "Select", value)
            self.emulator_tree.item(item_id, tags=("checked" if checked else "unchecked",))
        
        # Configure tag styles
        self.emulator_tree.tag_configure("checked")  # light green

    def toggle_select_all(self):
        """Toggle between selecting and unselecting all checkboxes in the TreeView."""
        # Check if all are currently selected (more efficient than checking all values)
        all_selected = all(self.selected_emulators.values()) if self.selected_emulators else False
        
        # Determine new state (invert current "all selected" state)
        new_state = not all_selected
        
        # Update all checkboxes and selection states
        for item_id in self.emulator_tree.get_children():
            self.selected_emulators[item_id] = new_state
        
        # Update visual display (this will handle both checkboxes and row coloring)
        self.update_checkbox_display()
        
        # Update button text
        self.select_all_button.config(text="Unselect All" if new_state else "Select All")

    def start_selected_players(self):
        """Start MuMuPlayer for all checked players, with enhanced status handling."""
        selected_players = set()
        running_players = set()
        invalid_players = set()

        # First pass: Collect all selected players and check their statuses
        for item_id in self.emulator_tree.get_children():
            if not self.selected_emulators.get(item_id, False):
                continue  # Skip unchecked items
                
            values = self.emulator_tree.item(item_id, "values")
            try:
                player_index = int(values[1])  # "No" column
                status = values[3]  # Status column
                
                print(f"🔍 Checking player {player_index} with status '{status}'")
                
                if status == "Running":
                    running_players.add(player_index)
                else:
                    selected_players.add(player_index)
            except (ValueError, IndexError):
                invalid_players.add(item_id)

        # Show appropriate warnings
        messages = []
        if not selected_players and not running_players:
            messages.append("No valid players selected!")
        if running_players:
            messages.append(f"Skipped {len(running_players)} already running players")
        if invalid_players:
            messages.append(f"Skipped {len(invalid_players)} invalid players")
        
        if messages:
            messagebox.showwarning("Selection Info", "\n".join(messages))
            if not selected_players:
                return

        # Start selected emulators with progress feedback
        self._show_starting_progress(len(selected_players))

    def _show_starting_progress(self, count):
        """Show progress for emulator startup."""
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
            
        self.progress_window = ttkb.Toplevel(self.master)
        self.progress_window.title("Starting Emulators")
        self.progress_window.geometry("300x100")
        self.progress_window.resizable(False, False)
        
        ttkb.Label(
            self.progress_window, 
            text=f"Starting {count} emulator{'s' if count > 1 else ''}..."
        ).pack(pady=10)
        
        self.progress_bar = ttkb.Progressbar(
            self.progress_window, 
            orient="horizontal", 
            length=250, 
            mode="indeterminate"
        )
        self.progress_bar.pack()
        self.progress_bar.start()
    
    def stop_selected_players(self):
        """Stop all selected emulators concurrently."""
        selected_players = []

        # ✅ Get checked emulators from TreeView
        for item_id in self.emulator_tree.get_children():
            values = self.emulator_tree.item(item_id, "values")
            checkbox_state = values[0]  # ✅ Checkbox state (☑ or ☐)
            display_no = int(values[1])  # ✅ "No" column (1-based index)
            status = values[3]  # ✅ Status column (Running or Not Running)

            if checkbox_state == "☑" and status == "Running":  # ✅ Stop only running emulators
                actual_index = display_no - 1  # ✅ Convert "No" to real index
                selected_players.append(actual_index)

        if not selected_players:
            messagebox.showwarning("Selection Error", "No running players selected!")
            return

        # ✅ Stop selected emulators **in parallel**
        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(self.emulator.stop_emulator, selected_players)

        # ✅ Refresh emulator list after stopping
        self.load_players()

    def select_all_emulators(self):
        """Toggle between selecting and unselecting all checkboxes in the TreeView."""
        all_selected = all(self.selected_emulators.values())  # Check if all are selected

        if all_selected:
            # Uncheck all
            for item_id in self.emulator_tree.get_children():
                current_values = self.emulator_tree.item(item_id, "values")
                self.emulator_tree.item(item_id, values=("☐",) + current_values[1:])  # Uncheck all
                self.selected_emulators[item_id] = False  # Mark as deselected

            self.select_all_button.config(text="Select All")  # Update button text
        else:
            # Check all
            for item_id in self.emulator_tree.get_children():
                current_values = self.emulator_tree.item(item_id, "values")
                self.emulator_tree.item(item_id, values=("☑",) + current_values[1:])  # Check all
                self.selected_emulators[item_id] = True  # Mark as selected

            self.select_all_button.config(text="Unselect All")  # Update button text

    def _update_emulator_status(self):
        """Fetch and update emulator status using parallel execution."""
        
        if not self.emulator_tree.get_children():
            print("ℹ️ No emulators found in TreeView.")
            return

        def fetch_status(item_id):
            """Helper function to fetch emulator status safely."""
            values = self.emulator_tree.item(item_id, "values")
            display_no = int(values[1])  # Convert "No" to integer
            emulator_index = display_no - 1  # Convert 1-based No to 0-based index
            
            status_info = self.emulator.get_emulator_status(emulator_index)

            # Ensure response is valid
            if not status_info:
                return item_id, {"status": "Unknown", "device_id": "Not Available"}

            return item_id, status_info

        # ✅ Run tasks in parallel for fast status updates
        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(executor.map(fetch_status, self.emulator_tree.get_children()))

        # ✅ Schedule UI updates to prevent threading issues
        def update_ui():
            for item_id, status_info in results:
                values = self.emulator_tree.item(item_id, "values")
                current_status = values[3]  # Current status in TreeView
                new_status = status_info.get("status", "Unknown")
                device_id = status_info.get("device_id", "Not Available")

                # ✅ Update UI only if status changed (Reduces UI updates)
                if current_status != new_status:
                    print(f"🔄 Updating {values[1]}: {device_id} -> {new_status}")
                    self.emulator_tree.item(item_id, values=(values[0], values[1], device_id, new_status))

        self.master.after(100, update_ui)  # ✅ Queue UI updates in the main thread

        # ✅ Schedule the next update
        self.master.after(2000, self._update_emulator_status)  # 🔄 Runs every 2 sec

    def sort_emulators(self):
        """Sort & arrange all emulator windows at the same time."""
        print("🔄 Sorting & Arranging Emulator Windows...")

        with ThreadPoolExecutor(max_workers=25) as executor:  # ✅ Run tasks in parallel
            executor.submit(self.emulator.arrange_windows)  # ✅ Arrange all windows concurrently
    
    def start_register_action(self):
        # Determine the base path for the 'screenshots' folder
        if getattr(sys, 'frozen', False):
            # Running as a PyInstaller executable
            # The 'screenshots' folder will be extracted to sys._MEIPASS
            screenshots_base_path = os.path.join(sys._MEIPASS, "screenshots")
        else:
            # Running as a normal Python script (development mode)
            # Assumes 'screenshots' folder is in the same directory as your main script
            screenshots_base_path = "screenshots" # Or os.path.join(os.getcwd(), "screenshots")

        # Ensure the screenshots directory exists.
        # It's good practice to create it if it doesn't, especially for development or if
        # it's a place where the app saves dynamic files.
        # If 'screenshots' is meant to be a user-writable directory (e.g., for saving emulator screenshots),
        # consider placing it in a user-specific data directory, not bundled with the app.
        # For now, we'll assume it's for temporary files related to the app's execution.
        if not os.path.exists(screenshots_base_path):
            os.makedirs(screenshots_base_path, exist_ok=True)
            print(f"Created screenshots directory: {screenshots_base_path}")
            # If the directory just got created, it's empty, so no need to list/delete
            return # Exit if it was just created, as there's nothing to delete.

        # Delete all files in the 'screenshots' folder
        print(f"Clearing contents of: {screenshots_base_path}")
        for filename in os.listdir(screenshots_base_path): # Use the corrected path
            file_path = os.path.join(screenshots_base_path, filename) # Use the corrected path for joining
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) # Remove file or link
                    print(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path) # Remove directory and its contents
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        """Start Facebook registration on selected emulators in parallel, ensuring UI remains responsive."""
        
        
        #If Gmail is selected, set num_rounds to 1
        if self.selected_mail.get() == "gmail":
            num_rounds = 1
        else:
            num_rounds = 9999  # ✅ Number of registration rounds per emulator
            
        selected_devices = self.get_selected_devices()

        if not selected_devices:
            print("⚠️ No emulators selected for registration!")
            return

        print(f"🚀 Starting Facebook Registration on {len(selected_devices)} emulators for {num_rounds} rounds each...")

        self.running = True  # ✅ Allow stopping registration

        def register_on_device(device_id):
            """Handle registration task for a single device."""
            round_number = 0
            while self.running and round_number < num_rounds:
                print(f"🔄 Round {round_number + 1}/{num_rounds} on {device_id}...")

                # ✅ Update UI Status
                # ✅ Update UI Status in main thread
                self.update_device_status(device_id, "Registering...")

                if self.reg_gmail:
                    self.register_gmail_account(device_id)
                else:
                    self.register_facebook_account(device_id)  # ✅ Perform Facebook registration

                # ✅ Update UI After Completion
                self.update_device_status(device_id, "Completed ✅")

                round_number += 1
                time.sleep(1)  # ✅ Small delay to prevent CPU overload

        # ✅ Start tasks for all selected devices **in separate threads** to keep UI responsive
        for device_id in selected_devices:
            threading.Thread(target=register_on_device, args=(device_id,), daemon=True).start()

        print("🎉 Registration process started on all devices!")

    def stop_registration(self):
        """Stop all ongoing registration tasks."""
        self.running = False
        print("⏹️ Registration process stopped!")  

    def get_selected_devices(self, show_warnings=True):
        """
        Retrieves selected emulator devices from the GUI's emulator_tree with enhanced validation.
        
        Args:
            show_warnings (bool): Whether to show warning messages (default: True)
        
        Returns:
            list: A list of selected and valid device IDs, or None if error occurs
        """
        selected_devices = []
        invalid_devices = []
        available_count = 0
        
        try:
            # First get all device IDs that are checked
            for item_id in self.emulator_tree.get_children():
                if not self.selected_emulators.get(item_id, False):
                    continue  # Skip unchecked items
                    
                try:
                    values = self.emulator_tree.item(item_id, "values")
                    
                    
                    device_id = str(values[1]).strip()  # Device ID column
                    status = str(values[2]).strip() if len(values) > 1 else ""
                    
                    
                    if not device_id or status == "Not Available":
                        invalid_devices.append(f"Row {self.emulator_tree.index(item_id)+1}")
                    else:
                        selected_devices.append(
                            status
                        )
                        available_count += 1
                        
                except (IndexError, ValueError, AttributeError) as e:
                    invalid_devices.append(f"Row {self.emulator_tree.index(item_id)+1}")
                    if show_warnings:
                        print(f"⚠️ Error processing row: {e}")

            # Show warnings if requested
            if show_warnings:
                if invalid_devices:
                    print(f"⚠️ Skipped {len(invalid_devices)} invalid devices: {', '.join(invalid_devices)}")
                if not available_count:
                    print("⚠️ No valid emulators selected!")
                    
            return selected_devices if available_count else None

        except Exception as e:
            if show_warnings:
                print(f"⛔ Critical error getting devices: {e}")
            return None

    def update_device_status(self, device_id, status):
        """Update the status column of a device in the TreeView, ensuring UI updates occur in the main thread."""
        
        def update():
            for item in self.emulator_tree.get_children():
                values = self.emulator_tree.item(item, "values")
                if values[2] == device_id:  # ✅ Match Device ID column
                    self.emulator_tree.item(item, values=(values[0], values[1], device_id, status))
                    break  # ✅ Exit after finding the correct row

        self.master.after(0, update)  # ✅ Ensures UI updates happen in the main thread

    def start_register_gmail(self):
        #Set Reg Gmail to True
        self.reg_gmail = True
        self.start_register_action()

    def register_facebook_account(self, device_id):
        """Registers a new Facebook account using ADB commands."""
        print(f"📲 Registering Facebook on {device_id}...")

        selected_package = self.selected_package.get()
        print(f"🔥 Selected Mode: {selected_package}")
        
        if selected_package == "com.facebook.lite":
            self.register_lite(device_id,selected_package)
        if selected_package == "com.facebook.katana":
            self.register_katana(device_id,selected_package)
            
    def register_lite(self, device_id, selected_package):
        
        if self.selected_mail.get() == "five_sim":
            print("Five Sim Mode")
            self.register_five_sim_lite(device_id,selected_package)
            return
        
        em = ADBController(device_id)  # ✅ Initialize ADBController for the device
        
        em.run_adb_command(["shell", "pm", "clear", "com.facebook.lite"])
        
        em.open_app(selected_package)  # ✅ Open Facebook Lite app
        """Registers a new Facebook account using ADB commands."""
        print(f"📲 Registering Facebook on {device_id}...")
        
        
        
        self.update_device_status(device_id,"Waiting Meta Logo")
        meta_logo = em.wait_img("templates/lite/meta_logo.png")

        if( meta_logo == False):
            self.update_device_status(device_id,"Meta Logo Not Found")
            em.wait(10)
            return
        self.update_device_status(device_id,"Meta Logo Found")
        
        login_templates = em.detect_templates([
            "templates/lite/login_step/create_new_account.png",
            "templates/lite/login_step/create_new_account_1.png",
            "templates/lite/login_step/create_new_account_2.png",
            "templates/lite/login_step/join_facebook.png",
            "templates/lite/login_step/sign_up.png",
            "templates/lite/login_step/create_new_account_blue.png",
            "templates/lite/login_step/get_started.png"
        ])
        
        if "create_new_account.png" in login_templates or 'create_new_account_1.png' in login_templates or 'create_new_account_2.png' in login_templates or "join_facebook.png" in login_templates or "sign_up.png" in login_templates:
            self.update_device_status(device_id,"Create New Account")
            em.tap(270.0,857.9)
        
        
        if "create_new_account_blue.png" in login_templates:
            self.update_device_status(device_id,"Create New Account Blue")
            em.tap_img("templates/lite/login_step/create_new_account_blue.png")
        
        if "get_started.png" in login_templates:
            self.update_device_status(device_id,"Get Started")
            em.tap_img("templates/lite/get_started.png")
        
        
        detect_last_name_or_get_started = em.detect_templates(
            [
                "templates/lite/get_started.png",
                "templates/lite/no_create_account.png",
                "templates/lite/create_new_account.png",
                "templates/lite/last_name.png",
                "templates/lite/yes_create_account.png",
            ]
        )
        
        self.update_device_status(device_id,"Input Last Name or Get Started")
        if 'last_name.png' in detect_last_name_or_get_started:
            self.update_device_status(device_id,"Input Last Name")
        else:
            self.update_device_status(device_id,"Input Last Name")
            em.tap_imgs(["templates/lite/get_started.png","templates/lite/no_create_account.png","templates/lite/create_new_account.png","templates/lite/yes_create_account.png"])
        
        
        first_name, last_name, phone_number, password, alias_email, main_email, pass_mail = generate_info(provider=self.selected_mail.get()).values()
        
        self.update_device_status(device_id,"Input First Name")
        em.wait(1)
        em.send_text(first_name)
        
        em.tap_img("templates/lite/last_name.png")
        self.update_device_status(device_id,"Input Last Name")
        em.wait(1)
        em.send_text(last_name)
        em.wait(1)
        
        em.tap_img("templates/lite/next.png")
        self.update_device_status(device_id,"Next")
        
        invalid_name = em.detect_templates([
            "templates/lite/invalid.png", 
            "templates/lite/wrong_name.png",
            "templates/lite/set_date.png"])
        
        
        if "invalid.png" in invalid_name:
            self.update_device_status(device_id,"Invalid Name")
            em.wait(1)
            return
        
        if "wrong_name.png" in invalid_name:
            self.update_device_status(device_id,"Invalid First Name")
            em.tap_img("templates/lite/wrong_name.png")
            em.wait(1)
            em.send_text(first_name)
            em.wait(1)
            em.tap_img("templates/lite/next.png")
            em.wait(3)
        
        if "set_date.png" in invalid_name:
            self.update_device_status(device_id,"Set Age")
            
        
        em.tap_img("templates/lite/cancel_date.png")
        
        em.tap_img("templates/lite/next.png")
        em.wait(1)
        em.tap_img("templates/lite/next.png")
        
        
        em.wait_img("templates/lite/how_old_are_you.png")
        
        em.wait(1)
        random_year = random.randint(18, 48)
        em.send_text(random_year)
        
        em.tap_img("templates/lite/next.png")
        self.update_device_status(device_id,"Next")
        em.wait(2)
        em.tap_img("templates/lite/next.png")
        
        em.tap_img("templates/lite/ok_birthday.png")
        
        
        em.tap_img("templates/lite/male.png")
        
        em.tap_img("templates/lite/next.png")
        self.update_device_status(device_id,"Next")
        
        detected_sign_up = em.detect_templates(["templates/lite/what_is_your_email.png", "templates/lite/mobile_number.png","templates/lite/mobile_number_cursor.png"])
        
        if "what_is_your_email.png" in detected_sign_up:
            self.update_device_status(device_id, "Sign Up With Email")
            em.tap_img("templates/lite/sign_up_with_phone.png")
            em.tap_img("templates/lite/mobile_number.png",timeout=5)
            em.send_text(phone_number)
            em.wait(1)
            
            
        if "mobile_number.png" in detected_sign_up or  "mobile_number_cursor.png" in detected_sign_up:
            em.tap_img("templates/lite/mobile_number.png",timeout=5)
            self.update_device_status(device_id,"Set Phone")
            em.send_text(phone_number)
            em.wait(1)
            
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/lite/next.png")

        continue_create_account = em.detect_templates(["templates/lite/continue_create_account.png", "templates/lite/eye_img.png","templates/lite/password_textbox.png"])
        
        if 'continue_create_account.png' in continue_create_account:
            em.tap_img("templates/lite/continue_create_account.png")
        
        self.update_device_status(device_id,"Wait Password Textbox")
        if 'eye_img.png' in continue_create_account:
            self.update_device_status(device_id,"Password Textbox Found")

        if 'password_textbox.png' in continue_create_account:
            self.update_device_status(device_id,"Click Password Textbox")
            em.tap_img("templates/lite/password_textbox.png")

        em.wait(1)
        em.send_text(password)
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        self.update_device_status(device_id,"save")
        em.tap_img("templates/lite/save.png")
        
        self.update_device_status(device_id,"Detect Logged Account")
        detect_logged_as = em.detect_templates(["templates/lite/logged_as.png","templates/lite/agree.png"])
        if "logged_as.png" in detect_logged_as:
            self.update_device_status(device_id,"logged_as")
            em.wait(3)
            return
        
        if 'agree.png' in detect_logged_as:
            self.update_device_status(device_id,"agree")
            em.tap_img("templates/lite/agree.png")
            
            
        detected_t1 = em.detect_templates(
            [
                "templates/lite/cannot_create_account.png",
                "templates/lite/we_need_more_info.png",
                "templates/lite/i_dont_get_code.png",
                "templates/lite/make_sure.png",
                "templates/lite/before_send.png",
                "templates/lite/confirm_by_email_lite.png",
            ]
        )
        
        self.update_device_status(device_id,"Detect Spam")
        if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1:
            self.update_device_status(device_id,"Spam Device")
            return
        
        if "make_sure.png" in detected_t1:
            self.update_device_status(device_id,"Make Sure Device")
            em.tap_img("templates/lite/continue.png")
        
        if "before_send.png" in detected_t1:
            self.update_device_status(device_id,"try_another_way")
            em.tap_img("templates/lite/try_another_way.png")
            
            self.update_device_status(device_id,"confirm_by_email")
            em.tap_img("templates/lite/confirm_by_email.png")

        
        if "confirm_by_email_lite.png" in detected_t1:
            em.tap_img("templates/lite/confirm_by_email_lite.png")
            self.update_device_status(device_id,"email_textbox")
            em.tap_img("templates/lite/email_textbox.png")
            
            em.wait(1)
            if self.selected_reg_type.get() == "wait_mail":
                self.update_device_status(device_id,"Please Input Your Email")
                em.wait(99999)
                
            em.send_text(alias_email)
            self.update_device_status(device_id,"next_email")
            em.tap_img("templates/lite/next_email.png")

        if "i_dont_get_code.png" in detected_t1:
            self.update_device_status(device_id,"i_dont_get_code")
            em.tap_img("templates/lite/i_dont_get_code.png")
            
            em.tap_img("templates/lite/confirm_by_email.png")
            
            em.wait(2)
            if self.selected_reg_type.get() == "wait_mail":
                self.update_device_status(device_id,"Please Input Your Email")
                em.wait(99999)
            em.send_text(alias_email)
            em.wait(1)
            em.tap_img("templates/lite/next.png")
    
        verify_code_count = 0
        while True:
            if self.selected_mail.get() == 'custom':
                code = get_domain_confirm_code(primary_email=main_email, alias_email=alias_email, password=pass_mail)
            else:
                code = get_confirmation_code(provider=self.selected_mail.get(), primary_email=main_email, alias_email=alias_email, password=pass_mail)  
                  
            verify_code_count += 1
            if(verify_code_count == 30):
                return
            if str(code).isnumeric():
                print("Code Received: "+ code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}")
            em.wait(1)
            
        if "i_dont_get_code.png" in detected_t1:
            em.send_text(code)
            em.wait("templates/lite/next.png")  

        if "confirm_by_email_lite.png" in detected_t1:
            self.update_device_status(device_id,"click confirm_code_textbox")
            em.tap_img("templates/lite/confirm_code_textbox.png")
            em.wait(2)
            
            for char in code:
                em.send_text(char)
                em.wait(0.2)
            
            em.wait(1)
            
            em.tap_img("templates/lite/ok_confirm_code.png")
                
        self.update_device_status(device_id,"skip_add_profile")
        em.tap_img("templates/lite/skip_add_profile.png")
        
        em.wait(2)
        self.update_device_status(device_id,"skip_turn_on_contact")
        em.tap_img("templates/lite/skip_turn_on_contact.png")
        
        
        
        detect_wrong = em.detect_templates(
            [
                "templates/lite/something_went_wrong.png",
                "templates/lite/confirm_skip_contact.png"
            ]
        ,timeout=10)
        
        if "something_went_wrong.png" in detect_wrong:
            self.update_device_status(device_id,"Something Went Wrong")
            em.wait(2)
            em.run_adb_command(["shell", "am", "force-stop", "com.facebook.lite"])
            em.open_app(selected_package)
        
        if "confirm_skip_contact.png" in detect_wrong: 
            em.tap_img("templates/lite/confirm_skip_contact.png")

        self.update_device_status(device_id,"Detecting 180Days")
        detect_appeal = em.detect_templates(["templates/lite/appeal.png","templates/lite/something_went_wrong.png"],timeout=15)
        if "appeal.png" in detect_appeal:
            self.update_device_status(device_id,"appeal")
            em.wait(3)
            return
        
        uid = em.extract_lite_uid()
        
        self.update_device_status(device_id,uid)
        em.wait(3)
        
        self.db_service.save_user(uid=uid, password=password, two_factor="", email=alias_email, pass_mail=pass_mail, acc_type=f"No 2FA {self.selected_mail.get()}")
        self.update_device_status(device_id,"Data Saved")
        em.wait(2)
        
    def register_katana(self, device_id, selected_package):
        
        if self.selected_mail.get() == "five_sim":
            print("Five Sim Mode")
            self.register_five_sim(device_id,selected_package)
            return
        if self.selected_mail.get() == "gmail":
            print("Gmail Mode")
            self.register_gmail(device_id,selected_package)
            return

                
        em = ADBController(device_id)
        
        
        em.clear_facebook_data()
        
        em.open_app(selected_package)
        
        self.update_device_status(device_id,"Waiting Meta Logo")
        meta_logo = em.wait_img("templates/katana/meta_logo.png")
        
        self.update_device_status(device_id,"Meta Logo Found")

        if( meta_logo == False):
            self.update_device_status(device_id,"Meta Logo Not Found")
            em.wait(10)
            return
        
        self.update_device_status(device_id,"Waiting Login Step")
        
        em.tap_imgs([
            "templates/katana/login_step/create_new_account.png",
            "templates/katana/login_step/create_new_account1.png",
            "templates/katana/login_step/get_started.png",
        ])
        
        self.update_device_status(device_id,"Create New Account")

        
        detect_last_name_or_get_started = em.detect_templates([
            "templates/katana/get_started.png",
            "templates/katana/no_create_account.png",
            "templates/katana/create_new_account.png",
            "templates/katana/last_name.png"
        ])
        
        self.update_device_status(device_id,"Input Last Name or Get Started")
        if 'last_name.png' in detect_last_name_or_get_started:
            self.update_device_status(device_id,"Input Last Name")
        else:
            self.update_device_status(device_id,"Get Started")
            em.tap_imgs([
                "templates/katana/get_started.png",
                "templates/katana/no_create_account.png",
                "templates/katana/create_new_account.png"
            ])
        

        first_name, last_name, phone_number, password, alias_email, main_email, pass_mail = generate_info(provider=self.selected_mail.get()).values()

        self.update_device_status(device_id,"Input First Name")
        em.wait(2)
        em.send_text(first_name)
        
        em.tap_img("templates/katana/last_name.png")
        self.update_device_status(device_id,"Input Last Name")
        em.wait(1)
        em.send_text(last_name)
        em.wait(1)
        
        self.update_device_status(device_id,"Next Name")
        em.tap_img("templates/katana/next.png")
        
        
        invalid_name = em.detect_templates(
            [
                "templates/katana/invalid.png", 
                "templates/katana/wrong_name.png",
                "templates/katana/set_date.png"
            ]
        )
        
        
        if "invalid.png" in invalid_name:
            self.update_device_status(device_id,"Invalid Name")
            em.wait(1)
            return
        
        if "wrong_name.png" in invalid_name:
            self.update_device_status(device_id,"Invalid First Name")
            em.tap_img("templates/katana/wrong_name.png")
            em.wait(1)
            em.send_text(first_name)
            em.wait(1)
            em.tap_img("templates/katana/next.png")
            em.wait(3)
            em.tap(265.1,316.5)
            em.wait(1)  
            em.tap(265.1,316.5)  


        self.update_device_status(device_id,"Wait Set Date")
        em.wait_img("templates/katana/set_date.png")

        # Generate random birthdate
        year_random = random.randint(27, 35)
        month_random = random.randint(20, 40)
        day_random = random.randint(10, 30)
        
        
        self.update_device_status(device_id,"set year")
        for x in range(year_random):
            em.tap(383, 402)
            time.sleep(0.1)
            
        self.update_device_status(device_id,"set month")
        for x in range(month_random):
            em.tap(266, 404)
            time.sleep(0.1)
        
        self.update_device_status(device_id,"set date")
        for x in range(day_random):
            em.tap(146, 404)
            time.sleep(0.1)
            
        em.tap_img("templates/katana/set_date.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"Select Gender")
        em.tap_img("templates/katana/male.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        
        detected_sign_up = em.detect_templates([
            "templates/katana/what_is_your_email.png", 
            "templates/katana/mobile_number.png",
            "templates/katana/mobile_number_cursor.png"
        ])
        
        if "what_is_your_email.png" in detected_sign_up:
            self.update_device_status(device_id, "Sign Up With Email")
            em.tap_img("templates/katana/sign_up_with_phone.png")
            em.tap_img("templates/katana/mobile_number.png",timeout=5)
            em.send_text(phone_number)
            em.wait(1)
            
            
        if "mobile_number.png" in detected_sign_up or  "mobile_number_cursor.png" in detected_sign_up:
            em.tap_img("templates/katana/mobile_number.png",timeout=5)
            self.update_device_status(device_id,"Set Phone")
            em.send_text(phone_number)
            em.wait(1)
            
        
        self.update_device_status(device_id,"Next Phone")
        em.tap_img("templates/katana/next.png")

        continue_create_account = em.detect_templates(["templates/katana/continue_create_account.png", "templates/katana/eye_img.png","templates/katana/password_textbox.png"])
        
        if 'continue_create_account.png' in continue_create_account:
            em.tap_img("templates/katana/continue_create_account.png")
        
        self.update_device_status(device_id,"Wait Password Textbox")
        if 'eye_img.png' in continue_create_account:
            self.update_device_status(device_id,"Password Textbox Found")

        if 'password_textbox.png' in continue_create_account:
            self.update_device_status(device_id,"Click Password Textbox")
            em.tap_img("templates/katana/password_textbox.png")

        em.wait(1)
        em.send_text(password)
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        
        self.update_device_status(device_id,"Detect Logged Account")
        detect_logged_as = em.detect_templates(["templates/katana/logged_as.png","templates/katana/agree.png"])
        if "logged_as.png" in detect_logged_as:
            self.update_device_status(device_id,"logged_as")
            em.wait(3)
            return
        
        if 'agree.png' in detect_logged_as:
            self.update_device_status(device_id,"agree")
            em.tap_img("templates/katana/agree.png")
        
        
        detected_t1 = em.detect_templates(
            [
                "templates/katana/cannot_create_account.png",
                "templates/katana/we_need_more_info.png",
                "templates/katana/i_dont_get_code.png",
                "templates/katana/make_sure.png",
                "templates/katana/before_send.png",
                "templates/katana/appeal.png",
                "templates/katana/account_locked.png",
            ]
        )
        skip_idont_get_code = False
        
        self.update_device_status(device_id,"Detect Spam")
        if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1 or "appeal.png" in detected_t1:
            self.update_device_status(device_id,"Spam Device")
            return
        
        if "account_locked.png" in detected_t1:
            self.update_device_status(device_id,"Account Locked")
            return
        
        if "make_sure.png" in detected_t1:
            self.update_device_status(device_id,"Make Sure Device")
            em.tap_img("templates/katana/continue.png")
        
        if "before_send.png" in detected_t1:
            self.update_device_status(device_id,"try_another_way")
            em.tap_img("templates/katana/try_another_way.png")
            
            self.update_device_status(device_id,"confirm_by_email")
            em.tap_img("templates/katana/confirm_by_email.png")
            skip_idont_get_code = True


        if skip_idont_get_code == False:
            if self.selected_reg_type.get() == "novery":
                self.update_device_status(device_id,"Getting UID")
                uid = em.extract_facebook_uid()
                self.update_device_status(device_id,uid)
                em.wait(2)
                #Save To database
                self.db_service.save_user(uid=uid, password=password, two_factor="", email="", pass_mail="", acc_type="Novery")
                self.update_device_status(device_id,"Novery Acc Saved")
                return
                
            em.tap_img("templates/katana/i_dont_get_code.png",timeout=60)
            self.update_device_status(device_id,"i_dont_get_code")
            em.tap_img("templates/katana/confirm_by_email.png")
        

        em.tap_img("templates/katana/email.png")
        
        em.wait(1)
        
        if self.selected_reg_type.get() == "wait_mail":
            self.update_device_status(device_id,"Please Input Your Email")
            em.wait(99999)

        em.send_text(alias_email)
    
        em.wait(1)
        
        em.tap_img("templates/katana/next.png")
        
        
        verify_code_count = 0
        while True:
            if self.selected_mail.get() == 'custom':
                code = get_domain_confirm_code(primary_email=main_email, alias_email=alias_email, password=pass_mail)
            else:
                code = get_confirmation_code(provider=self.selected_mail.get(), primary_email=main_email, alias_email=alias_email, password=pass_mail)  
                  
            verify_code_count += 1
            
            if(verify_code_count == 20):
                return
            if str(code).isnumeric():
                print("Code Received: "+ code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}")
            em.wait(1)

        em.send_text(code)
        
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"skip_add_profile")
        em.tap_img("templates/katana/skip_add_profile.png")
        
        self.update_device_status(device_id,"Goto Personal Info")
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "fb://facewebmodal/f?href=https://accountscenter.facebook.com/password_and_security/two_factor"])
    
        detect_appeal1 = em.detect_templates(["templates/katana/appeal.png"],timeout=20)
        if "appeal.png" in detect_appeal1:
            self.update_device_status(device_id,"appeal")
            em.wait(3)
            return
        
        
        self.update_device_status(device_id,"Getting UID")
        uid = em.extract_facebook_uid()
        self.update_device_status(device_id,uid)
        em.wait(2)
        
        self.db_service.save_user(uid=uid, password=password, two_factor="", email=alias_email, pass_mail=pass_mail, acc_type="No 2FA")
        self.update_device_status(device_id,"Data Saved")
        
    def register_five_sim(self, device_id, selected_package):
        em = ADBController(device_id)
            
        credentials = self.get_email_credentials()
        api_key = self.get_api_key()
        country = self.get_country()
        operator = self.get_operator()
        if None in (credentials, api_key, country, operator):
            return
        
        five_sim_api = FiveSimAPI(api_key, country=country, operator=operator)
        print("Balance: ", five_sim_api.get_balance())
            
        em.clear_facebook_data()
        
        em.open_app(selected_package)
        
        self.update_device_status(device_id,"Waiting Meta Logo")
        meta_logo = em.wait_img("templates/katana/meta_logo.png")

        if( meta_logo == False):
            self.update_device_status(device_id,"Meta Logo Not Found")
            em.wait(10)
            return
        
        login_templates = em.detect_templates([
            "templates/katana/login_step/create_new_account.png",
            "templates/katana/login_step/create_new_account_1.png",
            "templates/katana/login_step/create_new_account_2.png",
            "templates/katana/login_step/join_facebook.png",
            "templates/katana/login_step/sign_up.png",
            "templates/katana/login_step/create_new_account_blue.png",
            "templates/katana/login_step/get_started.png"
        ])
        
        login_temp = [
            "templates/katana/login_step/create_new_account.png",
            "templates/katana/login_step/create_new_account_1.png",
            "templates/katana/login_step/create_new_account_2.png",
            "templates/katana/login_step/join_facebook.png",
            "templates/katana/login_step/sign_up.png",
            "templates/katana/login_step/create_new_account_blue.png",
            "templates/katana/login_step/get_started.png"
        ]
        
        
        if "create_new_account.png" in login_templates or 'create_new_account_1.png' in login_templates or 'create_new_account_2.png' in login_templates or "join_facebook.png" in login_templates or "sign_up.png" in login_templates:
            self.update_device_status(device_id,"Create New Account")
            em.wait(2)
            em.tap_imgs(login_temp)
        
        
        if "create_new_account_blue.png" in login_templates:
            self.update_device_status(device_id,"Create New Account Blue")
            em.tap_img("templates/katana/login_step/create_new_account_blue.png")
        
        if "get_started.png" in login_templates:
            self.update_device_status(device_id,"Get Started")
            em.tap_img("templates/katana/get_started.png")

        
        
        detect_last_name_or_get_started = em.detect_templates(["templates/katana/get_started.png","templates/katana/no_create_account.png","templates/katana/create_new_account.png","templates/katana/last_name.png"])
        
        self.update_device_status(device_id,"Input Last Name or Get Started")
        if 'last_name.png' in detect_last_name_or_get_started:
            self.update_device_status(device_id,"Input Last Name")
        else:
            self.update_device_status(device_id,"Input Last Name")
            em.tap_imgs(["templates/katana/get_started.png","templates/katana/no_create_account.png","templates/katana/create_new_account.png"])
        
        
        first_name, last_name, password, email = five_sim_generate_info(main_email=credentials.email)
        
        print(email)

        
        self.update_device_status(device_id,"Input First Name")
        em.wait(1)
        em.send_text(first_name)
        
        em.tap_img("templates/katana/last_name.png")
        self.update_device_status(device_id,"Input Last Name")
        em.wait(1)
        em.send_text(last_name)
        em.wait(1)
        
        self.update_device_status(device_id,"Next Name")
        em.tap_img("templates/katana/next.png")
        
        
        invalid_name = em.detect_templates(
            [
                "templates/katana/invalid.png", 
                "templates/katana/wrong_name.png",
                "templates/katana/set_date.png",
                "templates/katana/select_your_name.png",
            ]
        )
        
        
        if "invalid.png" in invalid_name:
            self.update_device_status(device_id,"Invalid Name")
            em.wait(1)
            return
        
        if "wrong_name.png" in invalid_name:
            self.update_device_status(device_id,"Invalid First Name")
            em.tap_img("templates/katana/wrong_name.png")
            em.wait(1)
            em.send_text(first_name)
            em.wait(1)
            em.tap_img("templates/katana/next.png")
            em.wait(3)
            em.tap(265.1,316.5)
            em.wait(1)  
            em.tap(265.1,316.5)  

        if "select_your_name.png" in invalid_name:
            self.update_device_status(device_id,"Select Your Name")
            em.tap_img("templates/katana/name_checkbox.png")
            self.update_device_status(device_id,"Next")
            em.tap_img("templates/katana/next.png")
        
        
        self.update_device_status(device_id,"Wait Set Date")
        em.wait_img("templates/katana/set_date.png")

        # Generate random birthdate
        year_random = random.randint(27, 35)
        month_random = random.randint(20, 40)
        day_random = random.randint(10, 30)
        
    
        self.update_device_status(device_id,"set year")
        for x in range(year_random):
            em.tap(383, 402)
            time.sleep(0.1)
            
        self.update_device_status(device_id,"set month")
        for x in range(month_random):
            em.tap(266, 404)
            time.sleep(0.1)
        
        self.update_device_status(device_id,"set date")
        for x in range(day_random):
            em.tap(146, 404)
            time.sleep(0.1)
            
        em.tap_img("templates/katana/set_date.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"Select Gender")
        em.tap_img("templates/katana/male.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        
        activation_id = 0 
        five_sim_number = 0
        self.update_device_status(device_id,"Getting Mobile Number")
        
        
        five_sim = five_sim_api.get_available_number()
        while five_sim is None:
            self.update_device_status(device_id,"No available number found, retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            five_sim_api.get_available_number()
        
        activation_id = five_sim[0]
        five_sim_number = five_sim[1]
        
        print(activation_id, five_sim_number)
        
        detected_sign_up = em.detect_templates(["templates/katana/what_is_your_email.png", "templates/katana/mobile_number.png","templates/katana/mobile_number_cursor.png"])
        
        if "what_is_your_email.png" in detected_sign_up:
            self.update_device_status(device_id, "Sign Up With Email")
            em.tap_img("templates/katana/sign_up_with_phone.png")
            em.tap_img("templates/katana/mobile_number.png",timeout=5)
            em.send_text(five_sim_number)
            em.wait(1)
            
            
        if "mobile_number.png" in detected_sign_up or  "mobile_number_cursor.png" in detected_sign_up:
            em.tap_img("templates/katana/mobile_number.png",timeout=5)
            self.update_device_status(device_id,"Set Phone")
            em.send_text(five_sim_number)
            em.wait(1)
            
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/katana/next.png")

        em.wait(3)
        
        invalid_number = True
        
        while invalid_number:
            continue_create_account = em.detect_templates(["templates/katana/continue_create_account.png", "templates/katana/eye_img.png","templates/katana/password_textbox.png","templates/katana/invalid_number.png"])
            
            if 'continue_create_account.png' in continue_create_account:
                em.tap_img("templates/katana/continue_create_account.png")
                invalid_number = False
            
            self.update_device_status(device_id,"Wait Password Textbox")
            if 'eye_img.png' in continue_create_account:
                self.update_device_status(device_id,"Password Textbox Found")
                invalid_number = False

            if 'password_textbox.png' in continue_create_account:
                self.update_device_status(device_id,"Click Password Textbox")
                em.tap_img("templates/katana/password_textbox.png",timeout=15)
                invalid_number = False
            
            if 'invalid_number.png' in continue_create_account:
                invalid_number = True
                self.update_device_status(device_id,"Invalid Phone")
                five_sim_api.ban_number(activation_id)
                five_sim_api.cancel_activation(activation_id)
                em.wait(1)
                
                em.tap(247.2,288.8)
                em.wait(1)
                
                em.tap_img("templates/katana/clear_phone_number.png")
                
                five_sim = None
                em.wait(1)
                
                while five_sim is None:
                    five_sim = five_sim_api.get_available_number()
                    
                    if five_sim is None:
                        self.update_device_status(device_id, "No available number found, retrying...")
                        time.sleep(5)  # Wait before retrying again

                # ✅ Now it's safe to unpack
                activation_id = five_sim[0]
                five_sim_number = five_sim[1]
                
                em.wait(1)
                em.send_text(five_sim_number)
                em.wait(1)
                
                self.update_device_status(device_id,"Next")
                em.tap_img("templates/katana/next.png")
            
            
        em.wait(1)
        em.send_text(password)
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"save")
        em.tap_img("templates/katana/save.png")
        
        self.update_device_status(device_id,"Detect Logged Account")
        detect_logged_as = em.detect_templates(["templates/katana/logged_as.png","templates/katana/agree.png"])
        if "logged_as.png" in detect_logged_as:
            self.update_device_status(device_id,"logged_as")
            em.wait(3)
            return
        
        if 'agree.png' in detect_logged_as:
            self.update_device_status(device_id,"agree")
            em.tap_img("templates/katana/agree.png")
        
        agree_step_repeat = True
        while agree_step_repeat:
            agree_step_repeat = False
            detected_t1 = em.detect_templates(
                [
                    "templates/katana/cannot_create_account.png",
                    "templates/katana/we_need_more_info.png",
                    "templates/katana/i_dont_get_code.png",
                    "templates/katana/make_sure.png",
                    "templates/katana/before_send.png",
                    "templates/katana/send_code_vai_sms.png",
                    "templates/katana/confirm_your_mobile.png",
                    "templates/katana/try_another_way.png",
                    "templates/katana/no_create_account.png",
                    "templates/katana/appeal.png",
                ]
            )
        
            self.update_device_status(device_id,"Detect Spam")
            if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1 or "appeal.png" in detected_t1:
                self.update_device_status(device_id,"Spam Device")
                five_sim_api.ban_number(activation_id)
                five_sim_api.cancel_activation(activation_id)
                return
            
            if "make_sure.png" in detected_t1 or 'confirm_your_mobile.png' in detected_t1:
                self.update_device_status(device_id,"Make Sure Device")
                em.tap_img("templates/katana/continue.png")
            
            if "before_send.png" in detected_t1:
                self.update_device_status(device_id,"try_another_way")
                em.tap_img("templates/katana/try_another_way.png")
                
            if "send_code_vai_sms.png" in detected_t1:
                self.update_device_status(device_id,"send_code_vai_sms")
                em.tap_img("templates/katana/send_code_vai_sms.png")  
                em.tap_img("templates/katana/continue.png",timeout=3) 
            
            if "try_another_way.png" in detected_t1:
                self.update_device_status(device_id,"try_another_way")
                em.tap_img("templates/katana/try_another_way.png")
                agree_step_repeat = True
            
            if "no_create_account.png" in detected_t1:
                self.update_device_status(device_id,"no_create_account")
                em.tap_img("templates/katana/no_create_account.png")
                agree_step_repeat = True
            

        self.update_device_status(device_id,"Timeout 60s Get SMS")      
        em.wait(8)  
        verify_code_count = 0
        while True:
            sms_code = five_sim_api.get_sms(activation_id)
            verify_code_count += 1
            if(verify_code_count == 60):
                five_sim_api.cancel_activation(activation_id)
                five_sim_api.ban_number(activation_id)
                self.update_device_status(device_id,"SMS Timeout")
                return
            if str(sms_code).isnumeric():
                print("Code Received: "+ sms_code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}")
            em.wait(2)

        self.update_device_status(device_id,f"SMS Code: {sms_code}")
        em.send_text(sms_code)
        em.wait(1)
        
        em.tap_img("templates/katana/next.png")
        
        em.wait_img("templates/katana/skip_add_profile.png",timeout=30)
        
        self.update_device_status(device_id,"skip_add_profile")
        em.tap_img("templates/katana/skip_add_profile.png",timeout=20)
        
        self.update_device_status(device_id,"Detect Appeal")
        detect_appeal = em.detect_templates(["templates/katana/appeal.png"],timeout=20)
        if "appeal.png" in detect_appeal:
            self.update_device_status(device_id,"appeal")
            em.run_adb_command(["shell", "svc", "wifi", "disable"])
            em.run_adb_command(["shell", "svc", "wifi", "enable"])
            self.update_device_status(device_id,"Reboot Emulator")
            em.wait(600)
            return
        
        self.update_device_status(device_id,"Goto Personal Info")

        
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "fb://facewebmodal/f?href=https://accountscenter.facebook.com/personal_info/contact_points"])
    
        self.update_device_status(device_id,"Detect Appeal")
        detect_appeal1 = em.detect_templates(["templates/katana/appeal.png"],timeout=5)
        if "appeal.png" in detect_appeal1:
            self.update_device_status(device_id,"appeal")
            em.run_adb_command(["shell", "svc", "wifi", "disable"])
            em.run_adb_command(["shell", "svc", "wifi", "enable"])
            em.wait(600)
            return
    
        self.update_device_status(device_id,"Add New Contact")
        em.tap_img("templates/katana/add_new_contact.png")
        
        self.update_device_status(device_id,"Add Email")
        em.tap_img("templates/katana/add_email.png")
        
        self.update_device_status(device_id,"profile_checkbox")
        em.tap_img("templates/katana/profile_checkbox.png")
        
        
        self.update_device_status(device_id,"enter_email")
        em.tap_img("templates/katana/enter_email.png")
        em.wait(1)
        
        em.send_text(email)
        
        em.wait(1)
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/katana/next_add_email.png")
        
        detect_get_confirm = em.detect_templates([
            "templates/katana/enter_confirmation_code.png",
            "templates/katana/try_other_way_what_app.png"
        ])
        
        if 'enter_confirmation_code.png' in detect_get_confirm:
            self.update_device_status(device_id,"Getting Confirmation Code")
            confirm_code_count = 0
            while True:
                confirm_code = zoho_api_get_security_code(email)
                confirm_code_count += 1
                if(confirm_code_count == 30):
                    return
                if str(confirm_code).isnumeric():
                    print("Code Received: "+ confirm_code)
                    break
                self.update_device_status(device_id,f"Waiting Verify Code: {confirm_code_count}")
                em.wait(2)
            
            em.tap_img("templates/katana/enter_confirmation_code.png")
            em.wait(1)
            em.send_text(confirm_code)
            em.wait(1)
            
            self.update_device_status(device_id,"next_add_email")
            em.tap_img("templates/katana/next_add_email.png")
            
            self.update_device_status(device_id,"close_add_mail")
            em.tap_img("templates/katana/close_add_mail.png")
            
            self.update_device_status(device_id,"contact_info")
            em.tap_img("templates/katana/contact_info.png")
            em.wait(1)
            
            self.update_device_status(device_id,"phone_img")
            em.tap_img("templates/katana/phone_img.png")
            
            self.update_device_status(device_id,"delete_number")
            em.tap_img("templates/katana/delete_number.png")
            
            self.update_device_status(device_id,"confirm_delete_number")
            em.tap_img("templates/katana/confirm_delete_number.png")
            
            #Getting Security Code
            
            security_code_count = 0
            while True:
                security_code = get_confirmation_code(provider="zoho", primary_email=credentials.email, alias_email=email, password=credentials.pass_mail)
                security_code_count += 1
                if(security_code_count == 30):
                    return
                if str(security_code).isnumeric():
                    print("Code Received: "+ security_code)
                    break
                self.update_device_status(device_id,f"Security Code: {security_code_count}")
                em.wait(2)
            
            self.update_device_status(device_id,f"Security Code: {security_code}")
            em.send_text(security_code)
            em.wait(2)
            
            self.update_device_status(device_id,"Click Continue")
            em.tap_img("templates/katana/continue_security_code.png")
            
            em.wait_img("templates/katana/number_deleted.png")
            self.update_device_status(device_id,"number_deleted")
            
            self.update_device_status(device_id,"Getting UID")
            uid = em.extract_facebook_uid()
            self.update_device_status(device_id,uid)
            em.wait(2)
            
            self.db_service.save_user(uid=uid, password=password, two_factor="", email=email, pass_mail="", acc_type="No 2FA")
            self.update_device_status(device_id,"Data Saved")
            
            five_sim_api.finish_number(activation_id)
            em.wait(2)
            
            
        
        self.update_device_status(device_id,"try_other_way_what_app")
        em.tap_img("templates/katana/try_other_way_what_app.png")
        
        
        self.update_device_status(device_id,"text_message_check_box")
        em.tap_img("templates/katana/text_message_check_box.png")
        
        self.update_device_status(device_id,"continue_text_message")
        em.tap_img("templates/katana/continue_text_message.png")
        
        
        self.update_device_status(device_id,"Timeout 60s Get SMS")        
        wait_sms_count = 0
        while True:
            last_sms_code = five_sim_api.get_latest_sms_code(activation_id)
            wait_sms_count += 1
            if(wait_sms_count == 320):
                five_sim_api.ban_number(activation_id)
                five_sim_api.cancel_activation(activation_id)
                return
            if str(last_sms_code).isnumeric() and last_sms_code != sms_code:
                print("Code Received: "+ last_sms_code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {wait_sms_count}")
            em.tap_img("templates/katana/get_new_code.png",timeout=2)
        
        self.update_device_status(device_id,f"Last SMS: {last_sms_code}")  
        em.tap_img("templates/katana/last_sms_code.png")
        em.wait(1)
        em.send_text(last_sms_code)
        em.wait(1)
        
        self.update_device_status(device_id,"continue_text_message")  
        em.tap_img("templates/katana/continue_text_message.png")
        
        confirm_code_count = 0
        while True:
            confirm_code = get_confirmation_code(provider="zoho", primary_email=credentials.email, alias_email=email, password=credentials.pass_mail)
            confirm_code_count += 1
            if(confirm_code_count == 30):
                return
            if str(confirm_code).isnumeric():
                print("Code Received: "+ confirm_code)
                break
            self.update_device_status(device_id,f"Confirm Code : {confirm_code_count}")
            em.wait(2)
        
        self.update_device_status(device_id,"enter_confirmation_code")  
        em.tap_img("templates/katana/enter_confirmation_code.png")
        em.wait(1)
        em.send_text(confirm_code)
        em.wait(1)
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/katana/next_add_email.png")
        
        self.update_device_status(device_id,"close_add_mail")
        em.tap_img("templates/katana/close_add_mail.png")
        
        self.update_device_status(device_id,"contact_info")
        em.tap_img("templates/katana/contact_info.png")
        em.wait(1)
        
        self.update_device_status(device_id,"phone_img")
        em.tap_img("templates/katana/phone_img.png")
        
        self.update_device_status(device_id,"delete_number")
        em.tap_img("templates/katana/delete_number.png")
        
        self.update_device_status(device_id,"confirm_delete_number")
        em.tap_img("templates/katana/confirm_delete_number.png")
        
        
        em.wait_img("templates/katana/number_deleted.png")
        self.update_device_status(device_id,"number_deleted")
        
        self.update_device_status(device_id,"Getting UID")
        uid = em.extract_facebook_uid()
        self.update_device_status(device_id,uid)
        em.wait(2)
        
        self.db_service.save_user(uid=uid, password=password, two_factor="", email=email, pass_mail="", acc_type="No 2FA")
        self.update_device_status(device_id,"Data Saved")
        
        five_sim_api.finish_number(activation_id)
        em.wait(2)

    def register_five_sim_lite(self, device_id, selected_package):
        em = ADBController(device_id)
        
        
        credentials = self.get_email_credentials()
        api_key = self.get_api_key()
        country = self.get_country()
        operator = self.get_operator()
        if None in (credentials, api_key, country, operator):
            return
        
        em.run_adb_command(["shell", "pm", "clear", "com.facebook.lite"])
        
        em.open_app(selected_package)
        
        self.update_device_status(device_id,"Waiting Meta Logo")
        meta_logo = em.wait_img("templates/lite/meta_logo.png")

        if( meta_logo == False):
            self.update_device_status(device_id,"Meta Logo Not Found")
            em.wait(10)
            return
        
        em.wait(2)
        self.update_device_status(device_id,"Tap Create Acccount")
        em.tap(265.1,838.2)
        
        em.wait(3)

        
        self.update_device_status(device_id,"Get Started")
        detect_last_name_or_get_started = em.detect_templates(["templates/lite/get_started.png","templates/lite/no_create_account.png","templates/lite/create_new_account.png","templates/lite/last_name.png"])
        
        self.update_device_status(device_id,"Input Last Name or Get Started")
        if 'last_name.png' in detect_last_name_or_get_started:
            self.update_device_status(device_id,"Input Last Name")
        else:
            self.update_device_status(device_id,"Input Last Name")
            em.tap_imgs(["templates/lite/get_started.png","templates/lite/no_create_account.png","templates/lite/create_new_account.png"])
        
        
        first_name, last_name, password, email = five_sim_generate_info(main_email=credentials.email)
        
        print(email)

        
        self.update_device_status(device_id,"Input First Name")
        em.wait(1)
        em.send_text(first_name)
        
        em.tap_img("templates/lite/last_name.png")
        self.update_device_status(device_id,"Input Last Name")
        em.wait(1)
        em.send_text(last_name)
        em.wait(1)
        
        self.update_device_status(device_id,"Next Name")
        em.tap_img("templates/lite/next.png")
        
        
        invalid_name = em.detect_templates(
            [
                "templates/lite/invalid.png", 
                "templates/lite/wrong_name.png",
                "templates/lite/set_date.png"
            ]
        )
        
        
        if "invalid.png" in invalid_name:
            self.update_device_status(device_id,"Invalid Name")
            em.wait(1)
            return
        
        if "wrong_name.png" in invalid_name:
            self.update_device_status(device_id,"Invalid First Name")
            em.tap_img("templates/lite/wrong_name.png")
            em.wait(1)
            em.send_text(first_name)
            em.wait(1)
            em.tap_img("templates/lite/next.png")
            em.wait(3)
            em.tap(265.1,316.5)
            em.wait(1)  
            em.tap(265.1,316.5)  

        
        self.update_device_status(device_id,"Wait Set Date")
        em.wait_img("templates/lite/set_date.png")

        em.tap_img("templates/lite/cancel_date.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        em.wait(2)
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        em.wait(2)
        em.wait_img("templates/lite/how_old_are_you.png")
        em.wait(1)
        em.tap(73.3,214.0)
        em.wait(1)
        
        #random number from 18 to 38
        year_random = random.randint(18, 38)
        em.send_text(year_random)
        em.wait(1)
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/ok_birthday.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        self.update_device_status(device_id,"Select Gender")
        em.tap_img("templates/lite/male.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        five_sim_api = FiveSimAPI(api_key, country=country, operator=operator)
        print("Balance: ", five_sim_api.get_balance())
        
        activation_id = 0 
        five_sim_number = 0
        self.update_device_status(device_id,"Getting Mobile Number")
        
        five_sim = five_sim_api.get_available_number()
        while five_sim is None:
            print("No available number found, retrying...")
            self.update_device_status(device_id,"No available number found, retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            five_sim = five_sim_api.get_available_number()
        
        activation_id = five_sim[0]
        five_sim_number = five_sim[1]
        
        print(activation_id, five_sim_number)
        
        detected_sign_up = em.detect_templates(["templates/lite/what_is_your_email.png", "templates/lite/mobile_number.png","templates/lite/mobile_number_cursor.png"])
        
        if "what_is_your_email.png" in detected_sign_up:
            self.update_device_status(device_id, "Sign Up With Email")
            em.tap_img("templates/lite/sign_up_with_phone.png")
            em.tap_img("templates/lite/mobile_number.png",timeout=5)
            em.send_text(five_sim_number)
            em.wait(1)
            
            
        if "mobile_number.png" in detected_sign_up or  "mobile_number_cursor.png" in detected_sign_up:
            em.tap_img("templates/lite/mobile_number.png",timeout=5)
            self.update_device_status(device_id,"Set Phone")
            em.send_text(five_sim_number)
            em.wait(1)
            
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/lite/next.png")

        invalid_number = True
        
        while invalid_number:
            continue_create_account = em.detect_templates(["templates/lite/continue_create_account.png", "templates/lite/eye_img.png","templates/lite/password_textbox.png","templates/lite/invalid_number.png"])
            
            if 'continue_create_account.png' in continue_create_account:
                em.tap_img("templates/lite/continue_create_account.png")
                invalid_number = False
            
            self.update_device_status(device_id,"Wait Password Textbox")
            if 'eye_img.png' in continue_create_account:
                self.update_device_status(device_id,"Password Textbox Found")
                invalid_number = False

            if 'password_textbox.png' in continue_create_account:
                self.update_device_status(device_id,"Click Password Textbox")
                em.tap_img("templates/lite/password_textbox.png")
                invalid_number = False
            
            if 'invalid_number.png' in continue_create_account:
                invalid_number = True
                self.update_device_status(device_id,"Invalid Phone")
                five_sim_api.ban_number(activation_id)
                five_sim_api.cancel_activation(activation_id)
                em.wait(1)
                
                em.tap(247.2,288.8)
                em.wait(1)
                
                em.tap_img("templates/lite/clear_phone_number.png")
                
                five_sim = None
                em.wait(1)
                
                while five_sim is None:
                    print("No available number found, retrying...")
                    self.update_device_status(device_id,"No available number found, retrying...")
                    time.sleep(5)  # Wait for 5 seconds before retrying
                    five_sim = five_sim_api.get_available_number()
                    
                    activation_id = five_sim[0]
                    five_sim_number = five_sim[1]
                
                em.wait(1)
                em.send_text(five_sim_number)
                em.wait(1)
                
                self.update_device_status(device_id,"Next")
                em.tap_img("templates/lite/next.png")
            
            
        em.wait(1)
        em.send_text(password)
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/lite/next.png")
        
        self.update_device_status(device_id,"save")
        em.tap_img("templates/lite/save.png")
        
        self.update_device_status(device_id,"Detect Logged Account")
        detect_logged_as = em.detect_templates(["templates/lite/logged_as.png","templates/lite/agree.png"])
        if "logged_as.png" in detect_logged_as:
            self.update_device_status(device_id,"logged_as")
            em.wait(3)
            return
        
        if 'agree.png' in detect_logged_as:
            self.update_device_status(device_id,"agree")
            em.tap_img("templates/lite/agree.png")
            
        detected_t1 = em.detect_templates(
            [
                "templates/lite/confirm_your_mobile_number.png",
                "templates/lite/cannot_create_account.png",
                "templates/lite/we_need_more_info.png",
            ]
        )
       
        self.update_device_status(device_id,"Detect Spam")
        if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1:
            self.update_device_status(device_id,"Spam Device")
            five_sim_api.ban_number(activation_id)
            five_sim_api.cancel_activation(activation_id)
            return
        
        if "confirm_your_mobile_number.png" in detected_t1:
            self.update_device_status(device_id,"Confirm Your Mobile Number")
            em.tap_img("templates/lite/send_code_vai_sms.png")
            em.wait(2)
            
            self.update_device_status(device_id,"Continue")
            em.tap_img("templates/lite/continue.png")
        
        # if "make_sure.png" in detected_t1 or 'confirm_your_mobile.png' in detected_t1:
        #     self.update_device_status(device_id,"Make Sure Device")
        #     em.tap_img("templates/lite/continue.png")
        
        # if "before_send.png" in detected_t1:
        #     self.update_device_status(device_id,"try_another_way")
        #     em.tap_img("templates/lite/try_another_way.png")
            
        # if "choose_account.png" in detected_t1:
        #     self.update_device_status(device_id,"choose_account")  
        #     em.tap_img("templates/lite/choose_account.png")
        
    
        #     self.update_device_status(device_id,"no_create_new_account") 
        #     em.tap_img("templates/lite/no_create_new_account.png")
        
        #     self.update_device_status(device_id,"send_code_vai_sms")
        #     em.tap_img("templates/lite/send_code_vai_sms.png")  
        #     em.tap_img("templates/lite/send_code.png") 
        
        # if "no_create_new_account.png" in detected_t1:
        #     self.update_device_status(device_id,"no_create_new_account")  
        #     em.tap_img("templates/lite/no_create_new_account.png")
        # if "templates/lite/confirm_by_email_lite.png" in detected_t1:
        #     self.update_device_status(device_id,"Wait SMS Textbox") 

        self.update_device_status(device_id,"Wait SMS Textbox")   
        em.wait_imgs(["templates/lite/sms_code_textbox.png", "templates/lite/enter_the_confirmation_code.png"],timeout=30)
        

        self.update_device_status(device_id,"Getting SMS....")      
        em.wait(8)  
        verify_code_count = 0
        while True:
            sms_code = five_sim_api.get_sms(activation_id)  
            verify_code_count += 1
            if(verify_code_count == 30):
                five_sim_api.cancel_activation(activation_id)
                return
            if str(sms_code).isnumeric():
                print("Code Received: "+ sms_code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}")
            em.wait(2)

        self.update_device_status(device_id,f"SMS Code: {sms_code}")
        
        
        code_text_box_template = em.detect_templates(["templates/lite/sms_code_textbox.png", "templates/lite/enter_the_confirmation_code.png"])
        
        if "enter_the_confirmation_code.png" in code_text_box_template:
            self.update_device_status(device_id,"Entering SMS Code")
            em.send_text(sms_code)
            em.wait(1)
            em.tap_img("templates/lite/next.png")

        else:
            self.update_device_status(device_id,"Entering SMS Code") 
            em.tap_img("templates/lite/sms_code_textbox.png")
            for char in sms_code:
                em.send_text(char)
                em.wait(0.2)
                
            em.wait(1)
            self.update_device_status(device_id,"ok_confirm_code")
            em.tap_img("templates/lite/ok_confirm_code.png")

        self.update_device_status(device_id,"Detect Appeal")
        em.wait_img("templates/lite/skip_add_profile.png",timeout=30)
            
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "https://www.facebook.com/settings", "com.facebook.lite"])
        
        #Close Facebook Lite App
        self.update_device_status(device_id,"Close Facebook Lite App")
        em.run_adb_command(["shell", "am", "force-stop", "com.facebook.lite"])
        em.wait(5)
        
        self.update_device_status(device_id,"Open Facebook Lite App")
        #Open Facebook Lite App
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "https://www.facebook.com/settings", "com.facebook.lite"])
        
        em.tap_img("templates/lite/allow_cookie.png",timeout=10)
        
        self.update_device_status(device_id,"Detect Appeal")
        detect_appeal1 = em.detect_templates(["templates/lite/help.png", "templates/lite/refresh.png","templates/lite/account_center.png"],timeout=30)
        if "help.png" in detect_appeal1 or "refresh.png" in detect_appeal1:
            self.update_device_status(device_id,"Appeal")
            em.wait(120)
            return
        
        if "account_center.png" in detect_appeal1:
            self.update_device_status(device_id,"Goto Account Center")
        
        
        self.update_device_status(device_id,"Account Center")
        em.tap_img("templates/lite/account_center.png",timeout=30)
        
        self.update_device_status(device_id,"personal_detail")
        em.tap_img("templates/lite/personal_detail.png",timeout=30)
        
        self.update_device_status(device_id,"contact_info")
        em.tap_img("templates/lite/contact_info.png",timeout=30)
        
        self.update_device_status(device_id,"add_new_contact")
        em.tap_img("templates/lite/add_new_contact.png",timeout=30)
        
        em.wait(1)
        
        self.update_device_status(device_id,"add_email")
        em.tap_img("templates/lite/add_email.png",timeout=30)
        
        em.wait(2)
        self.update_device_status(device_id,"Enter Email Address")
        em.tap_img("templates/lite/enter_email_address.png",timeout=30)
        em.wait(1)
        em.send_text(email)
        
        em.wait(1)
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/lite/next_add_email.png",timeout=30)
        
        self.update_device_status(device_id,"try_other_way_what_app")
        em.tap_img("templates/lite/try_other_way_what_app.png")
        
        
        em.tap_img("templates/lite/see_more.png")
        
        self.update_device_status(device_id,"text_message_check_box")
        em.tap_img("templates/lite/text_message_check_box.png")
        
        em.tap_img("templates/lite/continue_message.png")
        
        self.update_device_status(device_id,"Getting Last SMS")        
        wait_sms_count = 0
        while True:
            last_sms_code = five_sim_api.get_latest_sms_code(activation_id)
            wait_sms_count += 1
            if(wait_sms_count == 130):
                five_sim_api.ban_number(activation_id)
                five_sim_api.cancel_activation(activation_id)
                return
            if str(last_sms_code).isnumeric() and last_sms_code != sms_code:
                print("Code Received: "+ last_sms_code)
                break
            self.update_device_status(device_id,f"Getting Last SMS: {wait_sms_count}")
            em.wait(1)
            em.tap_img("templates/lite/get_new_code.png",timeout=2)
        
        self.update_device_status(device_id,f"Last SMS: {last_sms_code}")  
        em.tap_img("templates/lite/last_sms_code.png")
        em.wait(1)
        em.send_text(last_sms_code)
        em.wait(1)
        
        em.tap_img("templates/lite/continue_message.png")
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/lite/next_add_email.png")
        
        confirm_code_count = 0
        while True:
            confirm_code = zoho_api_get_confirmation_code(email)
            confirm_code_count += 1
            if(confirm_code_count == 30):
                return
            if str(confirm_code).isnumeric():
                print("Code Received: "+ confirm_code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {confirm_code_count}")
            em.wait(2)
        
        self.update_device_status(device_id,"enter_confirmation_code")  
        em.tap_img("templates/lite/enter_confirmation_code.png",timeout=10)
        em.wait(1)
        em.send_text(confirm_code)
        em.wait(1)
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/lite/next_add_email.png")
        
        self.update_device_status(device_id,"close_add_mail")
        em.tap_img("templates/lite/close_add_mail.png")
        
        em.wait(7)
        self.update_device_status(device_id,"phone_img")
        em.tap_img("templates/lite/phone_img.png")
        
        self.update_device_status(device_id,"delete_number")
        em.tap_img("templates/lite/delete_number.png")
        
        self.update_device_status(device_id,"confirm_delete_number")
        em.tap_img("templates/lite/confirm_delete_number.png")
        
        
        em.wait_img("templates/lite/number_deleted.png")
        self.update_device_status(device_id,"number_deleted")
        
        self.update_device_status(device_id,"Getting UID")
        uid = em.extract_lite_uid()
        self.update_device_status(device_id,uid)
        em.wait(2)
        
        self.db_service.save_user(uid=uid, password=password, two_factor="", email=email, pass_mail="", acc_type="No 2FA")
        self.update_device_status(device_id,"Data Saved")
        
        five_sim_api.finish_number(activation_id)
        em.wait(2)
        
    def get_2fa_code(self, two_factor_key):
        print(two_factor_key)
        try:
            # Remove spaces from the key
            key = two_factor_key.replace(" ", "")
            
            # Validate that the key is not empty or too short
            if not key or len(key) < 16:
                raise ValueError("Invalid 2FA key. It should be at least 16 characters long.")
            
            # Create a TOTP object using the key
            totp = pyotp.TOTP(key)
            
            # Get and return the current 2FA code
            return totp.now()

        except ValueError as ve:
            # Handle cases where the key is invalid
            print(f"2FA Error: {ve}")
            return None

        except Exception as e:
            # Handle any other unexpected errors
            print(f"An unexpected error occurred: {e}")
            return None
    
    def register_gmail(self, device_id, selected_package):
        em = ADBController(device_id)
            
        em.clear_facebook_data()
        
        em.open_app(selected_package)
    
        
        self.update_device_status(device_id,"Waiting Meta Logo")
        meta_logo = em.wait_img("templates/katana/meta_logo.png")

        if( meta_logo == False):
            self.update_device_status(device_id,"Meta Logo Not Found")
            em.wait(10)
            return
        
        login_templates = em.detect_templates([
            "templates/katana/login_step/create_new_account.png",
            "templates/katana/login_step/create_new_account_1.png",
            "templates/katana/login_step/create_new_account_2.png",
            "templates/katana/login_step/join_facebook.png",
            "templates/katana/login_step/sign_up.png",
            "templates/katana/login_step/create_new_account_blue.png",
            "templates/katana/login_step/get_started.png"
        ])
        
        login_temp = [
            "templates/katana/login_step/create_new_account.png",
            "templates/katana/login_step/create_new_account_1.png",
            "templates/katana/login_step/create_new_account_2.png",
            "templates/katana/login_step/join_facebook.png",
            "templates/katana/login_step/sign_up.png",
            "templates/katana/login_step/create_new_account_blue.png",
            "templates/katana/login_step/get_started.png"
        ]
        
        
        if "create_new_account.png" in login_templates or 'create_new_account_1.png' in login_templates or 'create_new_account_2.png' in login_templates or "join_facebook.png" in login_templates or "sign_up.png" in login_templates:
            self.update_device_status(device_id,"Create New Account")
            em.wait(2)
            em.tap_imgs(login_temp)
        
        
        if "create_new_account_blue.png" in login_templates:
            self.update_device_status(device_id,"Create New Account Blue")
            em.tap_img("templates/katana/login_step/create_new_account_blue.png")
        
        if "get_started.png" in login_templates:
            self.update_device_status(device_id,"Get Started")
            em.tap_img("templates/katana/get_started.png")

        
        
        detect_last_name_or_get_started = em.detect_templates(["templates/katana/get_started.png","templates/katana/no_create_account.png","templates/katana/create_new_account.png","templates/katana/last_name.png"])
        
        self.update_device_status(device_id,"Input Last Name or Get Started")
        if 'last_name.png' in detect_last_name_or_get_started:
            self.update_device_status(device_id,"Input Last Name")
        else:
            self.update_device_status(device_id,"Input Last Name")
            em.tap_imgs(["templates/katana/get_started.png","templates/katana/no_create_account.png","templates/katana/create_new_account.png"])
        
        
        first_name, last_name, phone_number, password, alias_email, main_email, pass_mail = generate_info(provider=self.selected_mail.get()).values()
    
        
        self.update_device_status(device_id,"Input First Name")
        em.wait(1)
        em.send_text(first_name)
        
        em.tap_img("templates/katana/last_name.png")
        self.update_device_status(device_id,"Input Last Name")
        em.wait(1)
        em.send_text(last_name)
        em.wait(1)
        
        self.update_device_status(device_id,"Next Name")
        em.tap_img("templates/katana/next.png")
        
        
        invalid_name = em.detect_templates(
            [
                "templates/katana/invalid.png", 
                "templates/katana/wrong_name.png",
                "templates/katana/set_date.png",
                "templates/katana/select_your_name.png",
            ]
        )
        
        
        if "invalid.png" in invalid_name:
            self.update_device_status(device_id,"Invalid Name")
            em.wait(1)
            return
        
        if "wrong_name.png" in invalid_name:
            self.update_device_status(device_id,"Invalid First Name")
            em.tap_img("templates/katana/wrong_name.png")
            em.wait(1)
            em.send_text(first_name)
            em.wait(1)
            em.tap_img("templates/katana/next.png")
            em.wait(3)
            em.tap(265.1,316.5)
            em.wait(1)  
            em.tap(265.1,316.5)  

        if "select_your_name.png" in invalid_name:
            self.update_device_status(device_id,"Select Your Name")
            em.tap_img("templates/katana/name_checkbox.png")
            self.update_device_status(device_id,"Next")
            em.tap_img("templates/katana/next.png")
        
        
        self.update_device_status(device_id,"Wait Set Date")
        em.wait_img("templates/katana/set_date.png")

        # Generate random birthdate
        year_random = random.randint(27, 35)
        month_random = random.randint(20, 40)
        day_random = random.randint(10, 30)
        
    
        self.update_device_status(device_id,"set year")
        for x in range(year_random):
            em.tap(383, 402)
            time.sleep(0.1)
            
        self.update_device_status(device_id,"set month")
        for x in range(month_random):
            em.tap(266, 404)
            time.sleep(0.1)
        
        self.update_device_status(device_id,"set date")
        for x in range(day_random):
            em.tap(146, 404)
            time.sleep(0.1)
            
        em.tap_img("templates/katana/set_date.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"Select Gender")
        em.tap_img("templates/katana/male.png")
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        detected_sign_up = em.detect_templates(["templates/katana/what_is_your_email.png", "templates/katana/mobile_number.png","templates/katana/mobile_number_cursor.png"])
        
        if "what_is_your_email.png" in detected_sign_up:
            self.update_device_status(device_id, "Sign Up With Email")
            em.tap_img("templates/katana/sign_up_with_phone.png")
            em.tap_img("templates/katana/mobile_number.png",timeout=5)
            em.send_text(phone_number)
            em.wait(1)
            
            
        if "mobile_number.png" in detected_sign_up or  "mobile_number_cursor.png" in detected_sign_up:
            em.tap_img("templates/katana/mobile_number.png",timeout=5)
            self.update_device_status(device_id,"Set Phone")
            em.send_text(phone_number)
            em.wait(1)
            
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/katana/next.png")

        invalid_number = True
        
        while invalid_number:
            continue_create_account = em.detect_templates(["templates/katana/continue_create_account.png", "templates/katana/eye_img.png","templates/katana/password_textbox.png","templates/katana/invalid_number.png"])
            
            if 'continue_create_account.png' in continue_create_account:
                em.tap_img("templates/katana/continue_create_account.png")
                invalid_number = False
            
            self.update_device_status(device_id,"Wait Password Textbox")
            if 'eye_img.png' in continue_create_account:
                self.update_device_status(device_id,"Password Textbox Found")
                invalid_number = False

            if 'password_textbox.png' in continue_create_account:
                self.update_device_status(device_id,"Click Password Textbox")
                em.tap_img("templates/katana/password_textbox.png",timeout=15)
                invalid_number = False
            
            if 'invalid_number.png' in continue_create_account:
                invalid_number = True
                self.update_device_status(device_id,"Invalid Phone")
                return
            
            
        em.wait(1)
        em.send_text(password)
        
        self.update_device_status(device_id,"next")
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"save")
        em.tap_img("templates/katana/save.png")
        
        self.update_device_status(device_id,"Detect Logged Account")
        detect_logged_as = em.detect_templates(["templates/katana/logged_as.png","templates/katana/agree.png"])
        if "logged_as.png" in detect_logged_as:
            self.update_device_status(device_id,"logged_as")
            em.wait(3)
            return
        
        if 'agree.png' in detect_logged_as:
            self.update_device_status(device_id,"agree")
            em.tap_img("templates/katana/agree.png")
        
        detected_t1 = em.detect_templates(
            [
                "templates/katana/cannot_create_account.png",
                "templates/katana/we_need_more_info.png",
                "templates/katana/i_dont_get_code.png",
                "templates/katana/make_sure.png",
                "templates/katana/before_send.png",
                "templates/katana/appeal.png"
            ]
        )
        skip_idont_get_code = False
        
        self.update_device_status(device_id,"Detect Spam")
        if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1 or "appeal.png" in detected_t1:
            self.update_device_status(device_id,"Spam Device")
            return
        
        if "make_sure.png" in detected_t1:
            self.update_device_status(device_id,"Make Sure Device")
            em.tap_img("templates/katana/continue.png")
        
        if "before_send.png" in detected_t1:
            self.update_device_status(device_id,"try_another_way")
            em.tap_img("templates/katana/try_another_way.png")
            
            self.update_device_status(device_id,"confirm_by_email")
            em.tap_img("templates/katana/confirm_by_email.png")
            skip_idont_get_code = True


        if skip_idont_get_code == False:
            em.tap_img("templates/katana/i_dont_get_code.png",timeout=60)
            self.update_device_status(device_id,"i_dont_get_code")
            em.tap_img("templates/katana/confirm_by_email.png")
        

        em.tap_img("templates/katana/email.png")
        
        
        rented_email = ""

        while True:
            rented_email = rent_gmail()
            if "No rented email" in rented_email:
                print("No rented email")
                self.update_device_status(device_id,"No rented email")
                em.wait(2)
                continue
            break
        
        print(rented_email)
        
        
        # quid = get_order()
        # em.wait(1)
        # print(quid)
        # email, latest_code = get_otp(quid)
        
        # print(email)
        
        em.wait(1)
        em.send_text(rented_email)
        em.wait(1)
        
        em.tap_img("templates/katana/next.png")
        
        
        em.wait(5)
        
        # verify_code_count = 0
        # while True:
            
        #     email, latest_code = get_otp(quid)
        #     code = latest_code
            
        #     verify_code_count += 1
            
        #     if(verify_code_count == 60):
        #         return
        #     if str(code).isnumeric():
        #         print("Code Received: "+ code)
        #         break
        #     self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}s")
        #     em.wait(1)
        
        

        
        
        verify_code_count = 0
        while True:
            
            latest_code = get_otp_stp(rented_email)
            code = latest_code
            
            verify_code_count += 1
            
            if(verify_code_count == 60):
                return
            if str(code).isnumeric():
                print("Code Received: "+ code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}s")
            em.wait(1)
        
        em.send_text(code)
        
        em.tap_img("templates/katana/next.png")
        
        self.update_device_status(device_id,"skip_add_profile")
        em.tap_img("templates/katana/skip_add_profile.png")
        
        em.wait_img("templates/katana/skip_add_profile.png",timeout=30)
        
        self.update_device_status(device_id,"skip_add_profile")
        em.tap_img("templates/katana/skip_add_profile.png",timeout=20)
        
        self.update_device_status(device_id,"Detect Appeal")
        detect_appeal = em.detect_templates(["templates/katana/appeal.png"],timeout=20)
        if "appeal.png" in detect_appeal:
            self.update_device_status(device_id,"appeal")
            return
        
        self.update_device_status(device_id,"Goto Personal Info")

        
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "fb://facewebmodal/f?href=https://accountscenter.facebook.com/personal_info/contact_points"])
    
        self.update_device_status(device_id,"Detect Appeal")
        detect_appeal1 = em.detect_templates(["templates/katana/appeal.png"],timeout=5)
        if "appeal.png" in detect_appeal1:
            self.update_device_status(device_id,"appeal")
            return
    
        self.update_device_status(device_id,"Add New Contact")
        em.tap_img("templates/katana/add_new_contact.png")
        
        self.update_device_status(device_id,"Add Email")
        em.tap_img("templates/katana/add_email.png")
        
        self.update_device_status(device_id,"profile_checkbox")
        em.tap_img("templates/katana/profile_checkbox.png")
        
        
        self.update_device_status(device_id,"enter_email")
        em.tap_img("templates/katana/enter_email.png")
        em.wait(1)
        
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        new_email = f"eth168+{first_name.lower()}{last_name.lower()}{random_suffix}@zohomail.com"
        
        em.send_text(new_email)
        
        em.wait(1)
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/katana/next_add_email.png")
        
        detect_get_confirm = em.detect_templates([
            "templates/katana/enter_confirmation_code.png",
            "templates/katana/try_other_way_what_app.png"
        ])
        
        if 'enter_confirmation_code.png' in detect_get_confirm:
            self.update_device_status(device_id,"Getting Confirmation Code")
            confirm_code_count = 0
            while True:
                confirm_code = zoho_api_get_security_code(new_email)
                confirm_code_count += 1
                if(confirm_code_count == 30):
                    return
                if str(confirm_code).isnumeric():
                    print("Code Received: "+ confirm_code)
                    break
                self.update_device_status(device_id,f"Waiting Verify Code: {confirm_code_count}")
                em.wait(2)
            
            em.tap_img("templates/katana/enter_confirmation_code.png")
            em.wait(1)
            em.send_text(confirm_code)
            em.wait(1)
            
            self.update_device_status(device_id,"next_add_email")
            em.tap_img("templates/katana/next_add_email.png")
            
            self.update_device_status(device_id,"close_add_mail")
            em.tap_img("templates/katana/close_add_mail.png")
            
            self.update_device_status(device_id,"contact_info")
            em.tap_img("templates/katana/contact_info.png")
            em.wait(1)
            
            self.update_device_status(device_id,"phone_img")
            em.tap_img("templates/katana/phone_img.png")
            
            self.update_device_status(device_id,"delete_number")
            em.tap_img("templates/katana/delete_number.png")
            
            self.update_device_status(device_id,"confirm_delete_number")
            em.tap_img("templates/katana/confirm_delete_number.png")
            
            #Getting Security Code
            
            security_code_count = 0
            while True:
                security_code = zoho_api_get_security_code(new_email)
                security_code_count += 1
                if(security_code_count == 30):
                    return
                if str(security_code).isnumeric():
                    print("Code Received: "+ security_code)
                    break
                self.update_device_status(device_id,f"Security Code: {security_code_count}")
                em.wait(2)
            
            self.update_device_status(device_id,f"Security Code: {security_code}")
            em.send_text(security_code)
            em.wait(2)
            
            self.update_device_status(device_id,"Click Continue")
            em.tap_img("templates/katana/continue_security_code.png")
            
            em.wait_img("templates/katana/number_deleted.png")
            self.update_device_status(device_id,"number_deleted")
            
            self.update_device_status(device_id,"Getting UID")
            uid = em.extract_facebook_uid()
            self.update_device_status(device_id,uid)
            em.wait(2)
            
            self.db_service.save_user(uid=uid, password=password, two_factor="", email=new_email, pass_mail="", acc_type="No 2FA")
            self.update_device_status(device_id,"Data Saved")
        
            em.wait(2)
            
        
        
        # self.update_device_status(device_id,"Timeout 60s Get SMS")        
        # wait_sms_count = 0
        # while True:
        #     email, latest_code = get_otp(quid)
        #     last_sms_code = latest_code
        #     wait_sms_count += 1
        #     if(wait_sms_count == 60):
        #         return
        #     if str(last_sms_code).isnumeric() and last_sms_code != code:
        #         print("Code Received: "+ last_sms_code)
        #         break
        #     self.update_device_status(device_id,f"Waiting Verify Code: {wait_sms_count}")
        #     em.wait(1)
        
        self.update_device_status(device_id,"Timeout 60s Get SMS")        
        wait_sms_count = 0
        while True:
            latest_code = get_otp_stp(rented_email)
            last_sms_code = latest_code
            wait_sms_count += 1
            if(wait_sms_count == 60):
                return
            if str(last_sms_code).isnumeric() and last_sms_code != code:
                print("Code Received: "+ last_sms_code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {wait_sms_count}")
            em.wait(1)
        
        self.update_device_status(device_id,f"Last SMS: {last_sms_code}")  
        em.tap_img("templates/katana/last_sms_code.png",timeout=10)
        em.wait(1)
        em.send_text(last_sms_code)
        em.wait(2)
        
        self.update_device_status(device_id,"continue_text_message")  
        em.tap_img("templates/katana/continue_text_message.png")
        
        confirm_code_count = 0
        while True:
            confirm_code = zoho_api_get_security_code(new_email)
            confirm_code_count += 1
            if(confirm_code_count == 30):
                return
            if str(confirm_code).isnumeric():
                print("Code Received: "+ confirm_code)
                break
            self.update_device_status(device_id,f"Confirm Code : {confirm_code_count}")
            em.wait(2)
        
        self.update_device_status(device_id,"enter_confirmation_code")  
        em.tap_img("templates/katana/enter_confirmation_code.png")
        em.wait(1)
        em.send_text(confirm_code)
        em.wait(1)
        
        self.update_device_status(device_id,"next_add_email")
        em.tap_img("templates/katana/next_add_email.png")
        
        self.update_device_status(device_id,"close_add_mail")
        em.tap_img("templates/katana/close_add_mail.png")
        
        self.update_device_status(device_id,"contact_info")
        em.tap_img("templates/katana/contact_info.png")
        em.wait(1)
        
        self.update_device_status(device_id,"phone_img")
        em.tap_img("templates/katana/phone_img.png")
        
        self.update_device_status(device_id,"delete_number")
        em.tap_img("templates/katana/delete_number.png")
        
        self.update_device_status(device_id,"confirm_delete_number")
        em.tap_img("templates/katana/confirm_delete_number.png")
        
        
        em.wait_img("templates/katana/number_deleted.png")
        self.update_device_status(device_id,"number_deleted")
        
        self.update_device_status(device_id,"Getting UID")
        uid = em.extract_facebook_uid()
        self.update_device_status(device_id,uid)
        em.wait(2)
        
        if self.two_factor_checked.get() == "true":
            em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "fb://facewebmodal/f?href=https://accountscenter.facebook.com/password_and_security/two_factor"])
            self.update_device_status(device_id,"Two Factor")
            em.tap_img("templates/katana/arrow_icon.png")
            
            em.tap_img("templates/katana/next.png")
            
            em.swipe(460.5,825.4,472.4,416.2)
            
            #Screen Shot QR CODE
            clipboard_2fa = em.image_to_2fa()
            print(clipboard_2fa)
            self.update_device_status(device_id,f"2FA Key: {clipboard_2fa}")  
            
            em.tap_img("templates/katana/next.png")
            
            self.update_device_status(device_id,"Waiting 2FA Code")
            two_factor_code_count = 0
            while True:
                self.update_device_status(device_id,f"Waiting 2FA Code:{two_factor_code_count}s")
                two_factor_code = self.get_2fa_code(clipboard_2fa)
                two_factor_code_count += 1
                if str(two_factor_code).isnumeric():
                    self.update_device_status(device_id, f"2FA Code Received {two_factor_code}")
                    print("Code Received: "+ two_factor_code)
                    break
                if(two_factor_code_count == 30):
                    return
                em.wait(1)
            
            em.tap_img("templates/katana/enter_two_factor_code.png")
            em.wait(1)
            em.send_text(two_factor_code)
            em.wait(1)
            em.tap_img("templates/katana/next.png")
            
            em.wait(1)
            em.send_text(password)
            
            em.tap_img("templates/katana/continue.png")
            
            
            self.db_service.save_user(uid=uid, password=password, two_factor="clipboard_2fa", email=new_email, pass_mail="", acc_type="2FA")
        else:
            self.db_service.save_user(uid=uid, password=password, two_factor="", email=new_email, pass_mail="", acc_type="No 2FA")
        self.update_device_status(device_id,"Data Saved")
        em.wait(2)
        
    def register_gmail_account(self, device_id):
        """Registers a new Facebook account using ADB commands."""
        print(f"📲 Registering Gmail on {device_id}...")
        
        em = ADBController(device_id)
        
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "https://accounts.google.com/signup", "-n", "com.android.chrome/com.google.android.apps.chrome.Main"])
        
        self.update_device_status(device_id,"Input First Name")
        em.tap_img("templates/gmail/input_first_name.png")
        em.wait(1)
        
        first_name, last_name, password, email = five_sim_generate_info(main_email="eth168@zohomail.com")
        
        random_number = random.randint(10300, 99399)
        gmail = f"{first_name.lower()}{last_name.lower()}{random_number}@gmail.com"
        print(gmail)
        
        em.send_text(f"{first_name.lower()}{last_name.lower()}")
        em.wait(2)
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/next.png")
        
        self.update_device_status(device_id,"Month")
        em.tap_img("templates/gmail/month.png")
        
        
        em.tap_img("templates/gmail/may.png")
        
        em.tap_img("templates/gmail/day.png")
        
        em.send_text(14)
        
        em.tap_img("templates/gmail/year.png")
        
        em.send_text(1997)
        
        em.tap_img("templates/gmail/gender.png")

        em.tap_img("templates/gmail/male.png")
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/next.png")
        
        api_key = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzUzMDgxMjgsImlhdCI6MTc0Mzc3MjEyOCwicmF5IjoiN2YyMTMyMjNmNTcxMjIwMTUzMjM2NDhhM2JiYjM1ZjciLCJzdWIiOjMxMzM0ODR9.aHYVLcrpXSBva917hFbtXAqMgppHuJ5c1yYRzqwEl7QAg8dgehZR7DaWqbbnGhRUThUZqpv6P6NwEDfNa9v2vxFJelwM-XMANchSqOd8vrSht-n1Z_6aLEWefwCYvRHbjT4z3lTB4kJ7X4hkVELiy03PjYvuhCdUGQeV_L0L53LRgrJ2aLi71mv6TZ7MKy7BfYzXmFMaiZ0azH5qbb6jaQR_REPR_1AD0gf4E5-Ue9DP66FunR1UIxtVImZV7Htd0YswQYoJe8-cOrbTlWRMbEoiGfsLjFm17TMj6Ol_tYsdl4d_L6NFWG2mrdd58xGMAM1nnwldzOalkYn1CRRPOg"
        
        five_sim_api = FiveSimAPI(api_key, country="cambodia", operator="virtual49", product = "google")
        print("Balance: ", five_sim_api.get_balance())
        
        self.update_device_status(device_id,"create_own_gmail")
        em.tap_img("templates/gmail/create_own_gmail.png",timeout=15)
        em.wait(2)
        em.send_text(f"{first_name.lower()}{last_name.lower()}{random_number}")
        
        em.wait(1)
        em.tap(441.0,949.8)
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/next.png",timeout=10)
        
        em.wait_img("templates/gmail/confirm_password.png")
        em.wait(1)

        em.send_text(password)
        em.wait(1)
        
        em.tap_img("templates/gmail/confirm_password.png")
        em.send_text(password)
        
        em.wait(1)
        em.tap(460.5,836.2)
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/password_next.png")
        
        
        self.update_device_status(device_id,"Phone Number")
        em.tap_img("templates/gmail/phone_number.png")
        
        five_sim = five_sim_api.get_available_number()
        while five_sim is None:
            self.update_device_status(device_id,"No available number found, retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            five_sim_api.get_available_number()
        
        activation_id = five_sim[0]
        five_sim_number = five_sim[1]
        
        print(activation_id, five_sim_number)
        
        em.send_text(five_sim_number)
        em.wait(1)
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/next.png")
        
        invalid_number = True
        
        while invalid_number:
            phone_number_step = em.detect_templates([
                "templates/gmail/invalid_number.png", 
                "templates/gmail/enter_code.png",
            ])
            
            if 'enter_code.png' in phone_number_step:
                invalid_number = False
                
            if 'invalid_number.png' in phone_number_step:
                invalid_number = True
                self.update_device_status(device_id,"Invalid Phone")
                five_sim_api.ban_number(activation_id)
                five_sim_api.cancel_activation(activation_id)
                
                em.long_press(435.2,496.5)
                em.tap_img("templates/gmail/select_all_number.png")
                em.wait(2)
                
                five_sim = None
                em.wait(1)
                
                while five_sim is None:
                    five_sim = five_sim_api.get_available_number()
                    
                    if five_sim is None:
                        self.update_device_status(device_id, "No available number found, retrying...")
                        time.sleep(5)  # Wait before retrying again

                activation_id = five_sim[0]
                five_sim_number = five_sim[1]
                em.wait(1)
                em.send_text(five_sim_number)
                self.update_device_status(device_id,"Next")
                em.tap_img("templates/gmail/next.png")
                em.wait(5)

        self.update_device_status(device_id,"Timeout 60s Get SMS")      
        em.wait(8)  
        verify_code_count = 0
        while True:
            sms_code = five_sim_api.get_sms(activation_id)
            verify_code_count += 1
            if(verify_code_count == 60):
                five_sim_api.cancel_activation(activation_id)
                five_sim_api.ban_number(activation_id)
                self.update_device_status(device_id,"SMS Timeout")
                return
            if str(sms_code).isnumeric():
                print("Code Received: "+ sms_code)
                break
            self.update_device_status(device_id,f"Waiting Verify Code: {verify_code_count}")
            em.wait(2)
        
        em.send_text(sms_code)
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/next.png")
        
        em.wait(3)
        
        em.tap_img("templates/gmail/skip_add_recovery.png")
        
        self.update_device_status(device_id,"Next")
        em.tap_img("templates/gmail/next.png")
        
        em.wait_img("templates/gmail/privacy_term.png")
        
        em.swipe(496.1,933.7,491.5,148.8,700)
        em.swipe(496.1,933.7,491.5,148.8,700)
        em.swipe(496.1,933.7,491.5,148.8,700)
        
        em.wait(2)
        
        self.update_device_status(device_id,"Agree")
        em.tap_img("templates/gmail/agree.png")
        em.wait(15)
        
        self.db_service.save_gmail_account(first_name=first_name.lower(),last_name = last_name.lower(),gmail=gmail,password=password)
        self.update_device_status(device_id,"Data Saved")
        
        five_sim_api.finish_number(activation_id)
        em.wait(3)