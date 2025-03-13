import random
import time
import ttkbootstrap as ttkb
from ttkbootstrap import Button
from tkinter import messagebox
from app.controllers.adb_controller import ADBController
from app.controllers.emulator_controller import MuMuPlayerController
from concurrent.futures import ThreadPoolExecutor
import threading
import ttkbootstrap as ttkb
from ttkbootstrap import Combobox
from tkinter import messagebox,StringVar,filedialog
from PIL import Image, ImageTk
import os
from app.services.mysql_service import MySQLService
from app.controllers.emulator_controller import MuMuPlayerController
from concurrent.futures import ThreadPoolExecutor
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils.user_generator import generate_info

class EmulatorView:
    def __init__(self, master):
        self.master = master
        self.emulator = MuMuPlayerController(self)  # ✅ Pass `self` (MainWindow) as a reference to EmulatorController
        self.selected_emulators = {}

        # ✅ Setup Emulator UI
        self.setup_emulator_ui()

    def setup_emulator_ui(self):
        """Setup the Emulator UI Components"""
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

        # ✅ Button Size for Start/Stop Icons
        button_size = (25, 25)
        
        # ✅ Load Start/Stop Icons
        try:
            self.start_photo = ImageTk.PhotoImage(Image.open(os.path.join("assets", "start_icon.png")).resize(button_size, Image.Resampling.LANCZOS))
            self.stop_photo = ImageTk.PhotoImage(Image.open(os.path.join("assets", "stop_icon.png")).resize(button_size, Image.Resampling.LANCZOS))
        except FileNotFoundError:
            messagebox.showerror("Error", "Start/Stop icon file not found.")

        # ✅ Start Button (Only starts non-running emulators)
        start_button = ttkb.Button(
            button_frame,
            image=self.start_photo,
            command=self.start_selected_players,
            style="success.Compact.TButton",
            width=20,
            padding=2
        )
        start_button.pack(side="left", padx=0, pady=0)

        # ✅ Stop Button (Only stops running emulators)
        stop_button = ttkb.Button(
            button_frame,
            image=self.stop_photo,
            command=self.stop_selected_players,
            style="danger.Compact.TButton",
            width=20,
            padding=2
        )
        stop_button.pack(side="left", padx=5, pady=0)

        # ✅ Load Sort Icon
        try:
            sort_image_path = os.path.join("assets", "sort_icon.png")  # Replace with actual image path
            sort_image = Image.open(sort_image_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.sort_photo = ImageTk.PhotoImage(sort_image)
        except FileNotFoundError:
            messagebox.showerror("Error", "Sort icon file not found.")

        # ✅ Sort Button (Arranges Emulator Windows)
        sort_button = ttkb.Button(
            button_frame,
            image=self.sort_photo,
            command=self.sort_emulators,
            style="info.Compact.TButton",
            width=20,
            padding=2
        )
        sort_button.pack(side="left", padx=5, pady=0)


        # ✅ Start Register Button
        self.start_register_button = ttkb.Button(
            button_frame, 
            text="Start Register", 
            command=self.start_register_action, 
            style="success.TButton"
        )
        self.start_register_button.pack(side="left", padx=5)


        # ✅ Select All Button (Toggles between Select/Unselect)
        self.select_all_button = ttkb.Button(
            emulator_frame, 
            text="Select All", 
            command=self.toggle_select_all, 
            style="primary.TButton"
        )
        self.select_all_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # ✅ Dictionary to store checkbox states
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
        self.emulator_tree.column("Select", width=5, minwidth=5, stretch=True, anchor="center")
        self.emulator_tree.column("No", width=5, minwidth=5, stretch=True, anchor="center")
        self.emulator_tree.column("Device", width=70, minwidth=70, stretch=True, anchor="center")
        self.emulator_tree.column("Status", width=120, minwidth=120, stretch=True, anchor="center")

        # ✅ Place TreeView inside the grid
        self.emulator_tree.grid(row=1, column=0, columnspan=5, sticky="nsew")

        # ✅ Ensure Parent Frame Expands with the Window
        emulator_frame.grid_rowconfigure(1, weight=1)
        emulator_frame.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # ✅ Add Scrollbar to TreeView
        emulator_scrollbar = ttkb.Scrollbar(emulator_frame, orient="vertical", command=self.emulator_tree.yview)
        self.emulator_tree.configure(yscrollcommand=emulator_scrollbar.set)
        emulator_scrollbar.grid(row=1, column=5, sticky="ns")

        # ✅ Bind checkbox toggle function
        self.emulator_tree.bind("<ButtonRelease-1>", self.toggle_checkbox)

    def load_players(self):
        """Fetch player list and update TreeView efficiently."""
        self.emulator_tree.delete(*self.emulator_tree.get_children())  # ✅ Clear existing rows
        self.selected_emulators = {}  # ✅ Reset selection dictionary

        emulator_data = self.emulator.get_all_emulator_status()  # ✅ Get all emulator data

        if not emulator_data:
            self.emulator_tree.insert("", "end", values=("", "No Players Found", "", ""))
            return

        for idx, (player_index, data) in enumerate(emulator_data.items(), start=1):
            device_id = data["adb_port"] if data["adb_port"] else "Not Available"
            status = data["status"]

            # ✅ Insert into TreeView and store the item_id as a key
            item_id = self.emulator_tree.insert("", "end", values=("☐", idx, device_id, status))
            self.selected_emulators[item_id] = False  # ✅ Store item_id as a dictionary key

    def update_emulator_status_loop(self):
        """Continuously update emulator status in real-time using threading."""
        thread = threading.Thread(target=self._update_emulator_status, daemon=True)
        thread.start()

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

        # ✅ Get checked emulators from TreeView
        for item_id in self.emulator_tree.get_children():
            values = self.emulator_tree.item(item_id, "values")
            checkbox_state = values[0]  # ✅ Checkbox state
            display_no = int(values[1])  # ✅ "No" column (starts from 1)
            status = values[3]  # ✅ Status column (Running or Not Running)

            if checkbox_state == "☑" and status != "Running":
                actual_index = display_no - 1  # ✅ Convert "No" to real index
                selected_players.add(actual_index)  # ✅ Prevent duplicates

        if not selected_players:
            messagebox.showwarning("Selection Error", "No players selected or all are already running!")
            return

        # ✅ Start selected emulators in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:  # ✅ Use 5 workers to prevent overload
            results = list(executor.map(self.emulator.start_emulator, selected_players))

        # ✅ Refresh emulator list after starting
        self.master.after(2000, self.load_players)  # ✅ Delayed refresh to update status

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
                return item_id, {"status": "Unknown", "adb_port": "Not Available"}

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
                adb_port = status_info.get("adb_port", "Not Available")

                # ✅ Update UI only if status changed (Reduces UI updates)
                if current_status != new_status:
                    print(f"🔄 Updating {values[1]}: {adb_port} -> {new_status}")
                    self.emulator_tree.item(item_id, values=(values[0], values[1], adb_port, new_status))

        self.master.after(100, update_ui)  # ✅ Queue UI updates in the main thread

        # ✅ Schedule the next update
        self.master.after(2000, self._update_emulator_status)  # 🔄 Runs every 2 sec

    def sort_emulators(self):
        """Sort & arrange all emulator windows at the same time."""
        print("🔄 Sorting & Arranging Emulator Windows...")

        with ThreadPoolExecutor(max_workers=25) as executor:  # ✅ Run tasks in parallel
            executor.submit(self.emulator.arrange_windows)  # ✅ Arrange all windows concurrently
    
    def start_register_action(self):
        """Start Facebook registration on selected emulators in parallel, ensuring UI remains responsive."""
        num_rounds = 1  # ✅ Number of registration rounds per emulator
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

        controller = ADBController(device_id)

        print("🔥 Step 1: Clearing Facebook Data...")
        self.update_device_status(device_id, "Clearing Facebook data...")
        controller.clear_facebook_data()
        print(f"✅ Facebook data cleared on {device_id}")

        print("📲 Step 2: Opening Facebook App...")
        self.update_device_status(device_id, "Opening Facebook...")
        controller.open_facebook()
        print(f"✅ Facebook opened on {device_id}")
        
        # ✅ Click on "Create New Account" button
        print("🔍 Step 3: Detecting 'Create New Account' Button...")
        self.update_device_status(device_id, "Create New Account")
        controller.tap_img("templates/create_new_account.png", timeout=30)
        print(f"✅ 'Create New Account' button detected on {device_id}")
        
        
        templates_1 = [
            "templates/get_started.png",
            "templates/create_new_acoount_get_started.png",
            "templates/yes_create_account.png"
        ]
        

        # Run detection and tap the first matching template
        matched_template = controller.tap_multiple_templates(templates_1, timeout=20)

        if matched_template:
            print(f"🎯 Matched and tapped: {matched_template}")
        else:
            print("❌ No matching template found!")
            
        info = generate_info()

        # Unpacking dictionary keys into variables
        first_name, last_name, phone_number, password, alias_email, main_email, pass_mail = info.values()
            
        controller.wait(2)    
        self.update_device_status(device_id, "Input First Name...")
        controller.send_text(first_name)
        
        
        controller.tap_img("templates/last_name.png", timeout=30)
        
        self.update_device_status(device_id, "Input Last Name...")
        controller.send_text(last_name)
        
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/next.png", timeout=30)
        
        controller.tap_img("templates/set.png", timeout=30)
            
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/next.png", timeout=30)    
        
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/next.png", timeout=30)   
        
        controller.wait(3)
        self.update_device_status(device_id, "Input Age...")
        controller.send_text("28")    
        
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/next.png", timeout=30)  
            
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/ok_birthday.png", timeout=30)  
        
        
        self.update_device_status(device_id, "Male...")
        controller.tap_img("templates/male.png", timeout=30)
        
        
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/next.png", timeout=30)  
        
        
        self.update_device_status(device_id, "Input Phone Number...")
        controller.tap_img("templates/mobile_number.png", timeout=30)
        controller.send_text(phone_number)
        
        
        self.update_device_status(device_id, "next...")
        controller.tap_img("templates/next.png", timeout=30)  
        
        
        templates_2 = [
            "templates/eye_icon.png",
            "templates/continue_create_account.png",
        ]
      
        matched_template2 = controller.tap_multiple_templates(templates_2, timeout=20)
        
        if matched_template2 == "templates/eye_icon.png":
            controller.send_text(password)
            controller.tap_img("templates/next.png", timeout=30)
        
        if matched_template2 == "templates/continue_create_account.png":
            controller.tap_img("templates/continue_create_account.png", timeout=30)
            controller.wait(2)
            controller.send_text(password)
            controller.tap_img("templates/next.png", timeout=30)

        
        



