import random
import shutil
import time
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
from app.services.mysql_service import MySQLService
from app.controllers.emulator_controller import MuMuPlayerController
from concurrent.futures import ThreadPoolExecutor
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from app.utils.email_service import get_domain_confirm_code
from app.utils.five_sim import ban_number, cancel_activation, finish_number, get_available_number, get_latest_sms_code, get_sms
from app.utils.user_generator import generate_info
from app.utils.zoho import get_confirmation_code
from app.utils.zoho_api import zoho_api_get_confirmation_code
from app.utils.zoho_generate import generate_zoho_info

class EmulatorView:
    def __init__(self, master,db_service):
        self.master = master
        self.db_service = db_service
        self.emulator = MuMuPlayerController(self)  # ✅ Pass `self` (MainWindow) as a reference to EmulatorController
        self.selected_emulators = {}
        self.selected_package = tk.StringVar(value="com.facebook.katana")
        self.selected_mail = tk.StringVar(value="zoho")
        

        # ✅ Setup Emulator UI
        self.setup_emulator_ui()

    def setup_emulator_ui(self):
        """Setup the Emulator UI Components"""
        
        ICON_SIZE = (25, 25)  # Define constant for image resizing

        # ✅ Frame for Emulator Treeview
        emulator_frame = ttkb.Frame(self.master, padding=5)
        emulator_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # ✅ Ensure frame expands
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        emulator_frame.grid_rowconfigure(1, weight=1)  
        emulator_frame.grid_columnconfigure(0, weight=1)

        # ✅ Button Frame (Top of Emulator Tree)
        button_frame = ttkb.Frame(emulator_frame)
        button_frame.grid(row=0, column=0, padx=0, pady=10, sticky="w")

        # ✅ Function to Load Icons
        def load_icon(filename):
            try:
                return ImageTk.PhotoImage(Image.open(os.path.join("assets", filename)).resize(ICON_SIZE, Image.Resampling.LANCZOS))
            except FileNotFoundError:
                print(f"Warning: {filename} not found.")
                return None

        # ✅ Load Icons
        self.start_photo = load_icon("start_icon.png")
        self.stop_photo = load_icon("stop_icon.png")
        self.sort_photo = load_icon("sort_icon.png")

        # ✅ Start & Stop Buttons
        if self.start_photo:
            start_button = ttkb.Button(button_frame, image=self.start_photo, command=self.start_selected_players, style="success.Compact.TButton", width=20, padding=2)
            start_button.grid(row=0, column=0, padx=5)

        if self.stop_photo:
            stop_button = ttkb.Button(button_frame, image=self.stop_photo, command=self.stop_selected_players, style="danger.Compact.TButton", width=20, padding=2)
            stop_button.grid(row=0, column=1, padx=5)

        if self.sort_photo:
            sort_button = ttkb.Button(button_frame, image=self.sort_photo, command=self.sort_emulators, style="info.Compact.TButton", width=20, padding=2)
            sort_button.grid(row=0, column=2, padx=5)

        # ✅ Start Register Button (Moved to the same row as Change IMEI)
        self.start_register_button = ttkb.Button(button_frame, text="Start Register", command=self.start_register_action, style="success.TButton")
        self.start_register_button.grid(row=0, column=3, padx=5)

        self.change_imei_button = ttkb.Button(button_frame, text="Change IMEI", command=self.emulator.change_imei, style="success.TButton")
        self.change_imei_button.grid(row=0, column=5, padx=5)
        
                # ✅ Select All Button
        self.select_all_button = ttkb.Button(button_frame, text="Select All", command=self.toggle_select_all, style="primary.TButton")
        self.select_all_button.grid(row=0, column=6, padx=5, pady=5, sticky="nsew")

        # ✅ Frame for Mode Selection Checkboxes with Border
        register_frame = ttkb.Labelframe(button_frame, text="FB Selection", padding=5)
        register_frame.grid(row=1, column=0, columnspan=6, pady=(5, 0), sticky="w")

        # ✅ Lite Checkbox
        self.lite_checkbox = ttkb.Radiobutton(register_frame, text="Lite", variable=self.selected_package, value="com.facebook.lite", style="primary.TRadiobutton")
        self.lite_checkbox.grid(row=0, column=0, sticky="w", padx=5)

        # ✅ Katana Checkbox
        self.katana_checkbox = ttkb.Radiobutton(register_frame, text="Katana", variable=self.selected_package, value="com.facebook.katana", style="primary.TRadiobutton")
        self.katana_checkbox.grid(row=0, column=1, sticky="w", padx=5)
        
        self.chrome_checkbox = ttkb.Radiobutton(register_frame, text="Chrome", variable=self.selected_package, value="chrome", style="primary.TRadiobutton")
        self.chrome_checkbox.grid(row=0, column=2, sticky="w", padx=5)
        
        
        # ✅ Frame for Mode Selection Checkboxes with Border
        mode_selection_frame = ttkb.Labelframe(button_frame, text="Mail Selection", padding=5)
        mode_selection_frame.grid(row=2, column=0, columnspan=6, pady=(5, 0), sticky="w")

        self.zoho_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Zoho", variable=self.selected_mail, value="zoho", style="primary.TRadiobutton")
        self.zoho_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        
        self.yandex_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Yandex", variable=self.selected_mail, value="yandex", style="primary.TRadiobutton")
        self.yandex_checkbox.grid(row=0, column=1, sticky="w", padx=5)
        
        self.customer_email_checkbox = ttkb.Radiobutton(mode_selection_frame, text="Custom", variable=self.selected_mail, value="custom", style="primary.TRadiobutton")
        self.customer_email_checkbox.grid(row=0, column=2, sticky="w", padx=5)

        self.five_sim_checkbox = ttkb.Radiobutton(mode_selection_frame, text="5SIM", variable=self.selected_mail, value="five_sim", style="primary.TRadiobutton")
        self.five_sim_checkbox.grid(row=0, column=3, sticky="w", padx=5)



        # ✅ Dictionary to Store Checkbox States
        self.selected_emulators = {} 

        # ✅ Create Emulator TreeView
        self.emulator_tree = ttkb.Treeview(
            emulator_frame,
            columns=("Select", "No", "Device", "Status"),
            show="headings",
            height=15 
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
        self.emulator_tree.bind("<ButtonRelease-1>", self.toggle_checkbox)


    def load_players(self):
        """Fetch player list and update TreeView efficiently."""
        self.emulator_tree.delete(*self.emulator_tree.get_children())  # ✅ Clear existing rows
        self.selected_emulators = {}  # ✅ Reset selection dictionary

        emulator_data = self.emulator.get_all_emulator_status()  # ✅ Get all emulator data

        if not emulator_data:
            self.emulator_tree.insert("", "end", values=("", "No Players Found", "", ""))
            return

        for idx, (player_index, data) in enumerate(emulator_data.items(), start=0):
            device_id = data["device_id"] if data["device_id"] else "Not Available"
            status = data["status"]

            # ✅ Insert into TreeView and store the item_id as a key
            item_id = self.emulator_tree.insert("", "end", values=("☐", idx, device_id, status))
            self.selected_emulators[item_id] = False  # ✅ Store item_id as a dictionary key

    def toggle_checkbox(self, event):
        """Toggle checkbox state when a user clicks on the 'Select' column."""
        item_id = self.emulator_tree.identify_row(event.y)
        column = self.emulator_tree.identify_column(event.x)

        if column == "#1" and item_id:  # ✅ Check if click is in checkbox column
            current_values = self.emulator_tree.item(item_id, "values")
            checkbox_state = current_values[0]  # ✅ Get current checkbox state
            # ✅ Toggle checkbox state
            new_checkbox = "☑" if checkbox_state == "☐" else "☐"
            self.emulator_tree.item(item_id, values=(new_checkbox,) + current_values[1:])

            # ✅ Track selected emulators properly
            self.selected_emulators[item_id] = (new_checkbox == "☑")

            # ✅ Update "Select All" button dynamically
            all_selected = all(self.selected_emulators.values())  # ✅ Check if all are selected
            self.select_all_button.config(text="Unselect All" if all_selected else "Select All")

    def toggle_select_all(self):
        """Toggle between selecting and unselecting all checkboxes in the TreeView."""
        all_selected = all(self.selected_emulators.values())  # ✅ Check if all are selected

        new_checkbox = "☐" if all_selected else "☑"  # ✅ Toggle state

        # ✅ Apply new state to all rows
        for item_id in self.emulator_tree.get_children():
            current_values = self.emulator_tree.item(item_id, "values")
            self.emulator_tree.item(item_id, values=(new_checkbox,) + current_values[1:])
            self.selected_emulators[item_id] = (new_checkbox == "☑")

        # ✅ Update button text dynamically
        self.select_all_button.config(text="Unselect All" if new_checkbox == "☑" else "Select All")

    def start_selected_players(self):
        """Start MuMuPlayer for all checked players, but skip already running ones."""
        selected_players = set()  # Use a set to prevent duplicates

        # Loop through all rows in the TreeView
        for item_id in self.emulator_tree.get_children():
            values = self.emulator_tree.item(item_id, "values")
            checkbox_state = values[0]  # "☑" or "☐"
            display_no = int(values[1])  # "No" column; assuming it’s already the correct index
            status = values[3]  # Status column ("Running" or not)

            # Only add if the checkbox is checked and the emulator is not running
            if checkbox_state == "☑" and status != "Running":
                actual_index = display_no  # Use the number directly without subtracting 1
                selected_players.add(actual_index)

        if not selected_players:
            messagebox.showwarning("Selection Error", "No players selected or all are already running!")
            return

        # Start selected emulators in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(executor.map(self.emulator.start_emulator, selected_players))
        
        # Refresh emulator list after starting
        self.master.after(2000, self.load_players)

    def _get_treeview_item_by_no(self, no):
        """Find the TreeView item ID using the 'No' column."""
        for item_id in self.emulator_tree.get_children():
            values = self.emulator_tree.item(item_id, "values")
            if int(values[1]) == no:
                return item_id
        return None  # ✅ Return None if not found

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
        #delete all files in folder screenshots
        for filename in os.listdir("screenshots"):
            file_path = os.path.join("screenshots", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        """Start Facebook registration on selected emulators in parallel, ensuring UI remains responsive."""
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

    def get_selected_devices(self):
        """
        ✅ Retrieves selected emulator devices from the GUI’s emulator_tree.

        Returns:
            list: A list of selected device IDs.
        """
        selected_devices = []
        
        for item_id in self.emulator_tree.get_children():
            values = self.emulator_tree.item(item_id, "values")
            checkbox_state = values[0]  # First column is checkbox state
            device_id = values[2]  # Device ID column

            if checkbox_state == "☑" and device_id != "Not Available":
                selected_devices.append(device_id)

        if not selected_devices:
            print("⚠️ No emulators selected!")

        return selected_devices

    def update_device_status(self, device_id, status):
        """Update the status column of a device in the TreeView, ensuring UI updates occur in the main thread."""
        
        def update():
            for item in self.emulator_tree.get_children():
                values = self.emulator_tree.item(item, "values")
                if values[2] == device_id:  # ✅ Match Device ID column
                    self.emulator_tree.item(item, values=(values[0], values[1], device_id, status))
                    break  # ✅ Exit after finding the correct row

        self.master.after(0, update)  # ✅ Ensures UI updates happen in the main thread

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
        em = ADBController(device_id)  # ✅ Initialize ADBController for the device
        
        em.randomize_device_fingerprint()
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
        em.send_text(29)
        
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
            em.send_text(alias_email)
            self.update_device_status(device_id,"next_email")
            em.tap_img("templates/lite/next_email.png")

        if "i_dont_get_code.png" in detected_t1:
            self.update_device_status(device_id,"i_dont_get_code")
            em.tap_img("templates/lite/i_dont_get_code.png")
            
            em.tap_img("templates/lite/confirm_by_email.png")
            
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
        
        
        em = ADBController(device_id)
        
        # em.randomize_device_fingerprint()
        
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
            "templates/katana/login_step/join_facebook.png",
            "templates/katana/login_step/sign_up.png",
            "templates/katana/login_step/create_new_account_blue.png",
            "templates/katana/login_step/get_started.png"
        ],timeout=120)
        
        
        login_img = [
            "templates/katana/login_step/create_new_account.png",
            "templates/katana/login_step/join_facebook.png",
            "templates/katana/login_step/sign_up.png",
            "templates/katana/login_step/create_new_account_blue.png"
        ]
        
        if "create_new_account.png" in login_templates or "join_facebook.png" in login_templates or "sign_up.png" in login_templates:
            self.update_device_status(device_id,"Create Account Btn Found")
            em.wait(2)
            em.tap_imgs(login_img)
        
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
            self.update_device_status(device_id,"Get Started")
            em.tap_imgs(["templates/katana/get_started.png","templates/katana/no_create_account.png","templates/katana/create_new_account.png"])
        
        
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
            ]
        )
        skip_idont_get_code = False
        
        self.update_device_status(device_id,"Detect Spam")
        if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1:
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
        
        em.wait(1)
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
        
        
        first_name, last_name, phone_number, password, email = generate_zoho_info()

        
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
        
        
        activation_id = 0 
        five_sim_number = 0
        self.update_device_status(device_id,"Getting Mobile Number")
        
        five_sim = get_available_number()
        while five_sim is None:
            print("No available number found, retrying...")
            self.update_device_status(device_id,"No available number found, retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            five_sim = get_available_number()
        
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


        continue_create_account = em.detect_templates(["templates/katana/continue_create_account.png", "templates/katana/eye_img.png","templates/katana/password_textbox.png","templates/katana/invalid_number.png"])
        
        if 'continue_create_account.png' in continue_create_account:
            em.tap_img("templates/katana/continue_create_account.png")
        
        self.update_device_status(device_id,"Wait Password Textbox")
        if 'eye_img.png' in continue_create_account:
            self.update_device_status(device_id,"Password Textbox Found")

        if 'password_textbox.png' in continue_create_account:
            self.update_device_status(device_id,"Click Password Textbox")
            em.tap_img("templates/katana/password_textbox.png")
        
        if 'invalid_number.png' in continue_create_account:
            self.update_device_status(device_id,"Invalid Phone")
            ban_number(activation_id)
            cancel_activation(activation_id)
            em.wait(2)
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
        
        em.tap_img("templates/katana/no_create_account.png",timeout=10)
        
        detected_t1 = em.detect_templates(
            [
                "templates/katana/cannot_create_account.png",
                "templates/katana/we_need_more_info.png",
                "templates/katana/i_dont_get_code.png",
                "templates/katana/make_sure.png",
                "templates/katana/before_send.png",
                "templates/katana/send_code_vai_sms.png",
                "templates/katana/confirm_your_mobile.png"
            ]
        )
       
        self.update_device_status(device_id,"Detect Spam")
        if "cannot_create_account.png" in detected_t1 or "we_need_more_info.png" in detected_t1:
            self.update_device_status(device_id,"Spam Device")
            ban_number(activation_id)
            cancel_activation(activation_id)
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
        
    

        self.update_device_status(device_id,"Timeout 60s Get SMS")      
        em.wait(8)  
        verify_code_count = 0
        while True:
            sms_code = get_sms(activation_id)
            verify_code_count += 1
            if(verify_code_count == 30):
                cancel_activation(activation_id)
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
        
        
        detect_appeal = em.detect_templates(["templates/katana/appeal.png"],timeout=20)
        if "appeal.png" in detect_appeal:
            self.update_device_status(device_id,"appeal")
            em.wait(3)
            return
        
        self.update_device_status(device_id,"Goto Personal Info")

        
        em.run_adb_command(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "fb://facewebmodal/f?href=https://accountscenter.facebook.com/personal_info/contact_points"])
    
    
        detect_appeal1 = em.detect_templates(["templates/katana/appeal.png"],timeout=5)
        if "appeal.png" in detect_appeal1:
            self.update_device_status(device_id,"appeal")
            em.wait(3)
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
        
        
        self.update_device_status(device_id,"try_other_way_what_app")
        em.tap_img("templates/katana/try_other_way_what_app.png")
        
        
        self.update_device_status(device_id,"text_message_check_box")
        em.tap_img("templates/katana/text_message_check_box.png")
        
        self.update_device_status(device_id,"continue_text_message")
        em.tap_img("templates/katana/continue_text_message.png")
        
        
        self.update_device_status(device_id,"Timeout 60s Get SMS")        
        wait_sms_count = 0
        while True:
            last_sms_code = get_latest_sms_code(activation_id)
            wait_sms_count += 1
            if(wait_sms_count == 60):
                ban_number(activation_id)
                cancel_activation(activation_id)
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
        
        finish_number(activation_id)
        em.wait(2)
        
        
        
        
        
        
        
        
        
        


