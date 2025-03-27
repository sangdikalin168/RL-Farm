import json
import os
import random
import subprocess
import sys
import re
from tkinter import messagebox

# Fix for PyInstaller EXE: Ensure stdout and stderr are always available
if getattr(sys, 'frozen', False):  # Running as EXE
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

from concurrent.futures import ThreadPoolExecutor

class MuMuPlayerController:
    """Controller for managing MuMuPlayer emulator actions."""

    def __init__(self,view):
        self.view = view  # ✅ Reference to MainWindow (or EmulatorView)
        # ✅ Define MuMuPlayer executable path
        self.mumu_path = self.find_mumu_path()
        self.vms_path = os.path.join(self.mumu_path, "vms")
        self.mumu_manager_path = os.path.join(self.mumu_path, "shell", "MuMuManager.exe")
        self.adb_path = os.path.join(os.getcwd(), "adb", "adb.exe")
        self.device_id = "127.0.0.1:16416"  # ✅ Default ADB port for the first emulator  # Example: "127.0.0.1:16384"

    def find_mumu_path(self):
        """Find MuMuPlayer installation path dynamically."""
        possible_paths = [
            r"C:\\Program Files\\Netease\\MuMuPlayerGlobal-12.0",
            r"D:\\Program Files\\Netease\\MuMuPlayerGlobal-12.0"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        messagebox.showerror("Error", "MuMuPlayer installation not found!")
        # sys.exit("❌ MuMuPlayer installation not found!")

    def run_command(self, command):
        """Execute a command and return its output as a string."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip() if result.stdout else ""  # ✅ Ensure it always returns a string
        except subprocess.CalledProcessError as e:
            print(f"❌ Command Failed: {e.stderr.strip() if e.stderr else 'Unknown Error'}")
            return ""  # ✅ Return empty string on failure
        except FileNotFoundError:
            print("❌ Error: MuMuManager.exe not found!")
            return ""  # ✅ Ensure function never returns None

    def get_player_list(self):
        """Fetches the list of available MuMu Player instances."""
        try:
            command = [self.mumu_manager_path, "api", "get_player_list"]
            result = self.run_command(command)

            print(f"✅ Raw Player List Output: {result}")  # ✅ Debug log

            if "get player list:" not in result:
                print("❌ Failed to parse player list from output.")
                return []

            # ✅ Extract the list from output
            player_list_str = result.split("get player list:")[1].split("result:")[0].strip()

            # ✅ Use regex to filter only numeric values
            player_list = [int(index) for index in re.findall(r'\b\d+\b', player_list_str)]
            player_list.sort()  # ✅ Sort from smallest to largest
            
            return player_list

        except Exception as e:
            print(f"❌ Error in get_player_list: {str(e)}")
            return []

    def get_adb_port(self, index):
        """Retrieve the ADB port for a specific MuMuPlayer instance, ensuring it's running first."""
        state = self.get_emulator_status(index)

        if state != "Running":
            return None  # ✅ Skip if not running

        try:
            output = subprocess.run(
                [self.mumu_manager_path, "adb", "-v", str(index)],
                capture_output=True, text=True, check=True, timeout=2  # ✅ Add timeout for fast execution
            ).stdout.strip()

            if "127.0.0.1:" in output:
                return output  # ✅ Return valid ADB address
        except subprocess.TimeoutExpired:
            print(f"❌ ADB command timeout for emulator {index}")
        except subprocess.CalledProcessError as e:
            print(f"❌ ADB command failed for emulator {index}: {e}")

        return None

    def get_emulator_status(self, index):
        """Fetch ADB port and running status for a specific emulator."""
        try:
            # ✅ Ensure index is an integer before proceeding
            if not isinstance(index, int):
                print(f"❌ Invalid Emulator Index: {index} (Skipping)")
                return {"device_id": None, "status": "Unknown"}

            # ✅ Check if emulator is running
            status_result = self.run_command([self.mumu_manager_path, "api", "-v", str(index), "player_state"])

            if not status_result:
                print(f"❌ Error: Empty response for player {index}")
                return {"device_id": None, "status": "Unknown"}

            if "state=start_finished" in status_result:
                status = "Running"
            elif "player not running" in status_result or "result=-2" in status_result:
                return {"device_id": None, "status": "Not Running"}

            # ✅ Only get ADB port if emulator is running
            adb_result = self.run_command([self.mumu_manager_path, "adb", "-v", str(index)])

            if not adb_result:
                print(f"❌ Error: Empty ADB response for player {index}")
                return {"device_id": None, "status": "Not Running"}

            if "not running" in adb_result:
                return {"device_id": None, "status": "Not Running"}

            device_id = adb_result.strip()
            return {"device_id": device_id, "status": status}

        except Exception as e:
            print(f"❌ Exception in get_emulator_status({index}): {str(e)}")
            return {"device_id": None, "status": f"Error: {str(e)}"}

    def get_all_emulator_status(self):
        """Optimized: Only connect ADB for running players."""
        emulator_data = {}

        # ✅ Step 1: Get player list
        player_list = self.get_player_list()
        if not player_list:
            print("❌ No players found.")
            return {}

        # ✅ Step 2: Run "get adb port" commands in parallel
        adb_processes = {}
        for player in player_list:
            cmd = [self.mumu_manager_path, "adb", "-v", str(player)]
            adb_processes[player] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ✅ Step 3: Process ADB Port Results
        for player, process in adb_processes.items():
            stdout, stderr = process.communicate()
            device_id = stdout.strip() if "127.0.0.1" in stdout else None  # ✅ Extract port only if valid
            emulator_data[player] = {"device_id": device_id, "status": "Unknown"}

        # ✅ Step 4: Fetch Player State (Check if Running)
        state_processes = {}
        running_players = []  # ✅ Track running players to connect ADB only for them
        for player in player_list:
            cmd = [self.mumu_manager_path, "api", "-v", str(player), "player_state"]
            state_processes[player] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ✅ Step 5: Process Player States
        for player, process in state_processes.items():
            stdout, stderr = process.communicate()
            if "state=start_finished" in stdout:
                emulator_data[player]["status"] = "Running"
                running_players.append(player)  # ✅ Mark for ADB connection
            elif "player not running" in stdout or "result=-2" in stdout:
                emulator_data[player]["status"] = "Not Running"

        # ✅ Step 6: Connect ADB **Only for Running Players**
        adb_connect_processes = {}
        for player in running_players:  # ✅ Only connect for running players
            cmd = [self.mumu_manager_path, "adb", "-v", str(player), "connect"]
            adb_connect_processes[player] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return emulator_data

    def start_emulator(self, index):
        """Starts a MuMuPlayer emulator by index."""
        print(f"▶️ Starting Emulator {index}...")  # ✅ Debugging log

        try:
            # ✅ Run the MuMuManager command to start the emulator
            command = [self.mumu_manager_path, "api", "-v", str(index), "launch_player"]
            result = subprocess.run(command, capture_output=True, text=True)

            # ✅ Check if the emulator started successfully
            output = result.stdout.strip()
            if "result=0" in output:
                print(f"✅ Emulator {index} started successfully.")
            else:
                print(f"❌ Failed to start emulator {index}. Output: {output}")

        except Exception as e:
            print(f"❌ Command Failed: {e}")

    def stop_emulator(self, index):
        """
        Stop an emulator instance if it's running.

        Args:
            index (int): The emulator index.
        """
        try:
            # ✅ First, check if the emulator is running
            status = self.get_emulator_status(index)
            if status == "Not Running":
                print(f"⏹️ Emulator {index} is already stopped.")
                return
            
            # ✅ Shutdown Command
            command = [
                self.mumu_manager_path,
                "api",
                "-v",
                str(index),
                "shutdown_player"
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            print(f"✅ Emulator {index} stopped successfully: {result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop emulator {index}: {e.stderr}")

    def set_window_position(self, index, x, y, width, height):
        """Arrange a MuMu Player window at a specific position."""
        self.run_command([self.mumu_manager_path, "setting", "-v", str(index), "set_window_pos", f"{x},{y},{width},{height}"])

    def arrange_windows(self):
        GRID_COLS = 6
        WINDOW_WIDTH = 220
        WINDOW_HEIGHT = 425
        WINDOW_GAP = 0  # Gap between windows
        
        """Arrange running MuMu Player instances in a grid layout without reconnecting ADB."""
        print("🔄 Arranging MuMu Player Windows...")

        # ✅ Step 1: Get Player List
        player_list = self.get_player_list()
        if not player_list:
            print("❌ No players available to arrange.")
            return

        # ✅ Step 2: Fetch Emulator Status & ADB Ports in Parallel
        running_players = []
        emulator_data = {}

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = {executor.submit(self.get_emulator_status, idx): idx for idx in player_list}
            for future in futures:
                status_info = future.result()
                instance_index = futures[future]

                if status_info["status"] == "Running":
                    running_players.append(instance_index)
                    emulator_data[instance_index] = status_info  # ✅ Store status & ADB info

        if not running_players:
            print("❌ No running players to arrange.")
            return

        # ✅ Step 3: Arrange Running Players in Grid (No ADB Reconnection)
        def arrange_window(instance_index, idx):
            """Arrange a single window in the grid."""
            row = idx // GRID_COLS
            col = idx % GRID_COLS
            x = col * (WINDOW_WIDTH + WINDOW_GAP)
            y = row * (WINDOW_HEIGHT + WINDOW_GAP)
            self.set_window_position(instance_index, x, y, WINDOW_WIDTH, WINDOW_HEIGHT)

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(arrange_window, running_players, range(len(running_players)))

        print(f"✅ Successfully arranged {len(running_players)} players.")

    def run_adb_command(self, command, as_root=False):
        """Run an ADB command with optional root privileges."""
        try:
            full_command = [self.adb_path, "-s", self.device_id, "shell"]
            if as_root:
                full_command += ["su", "-c"]  # Run with root
            full_command += command  # Append the actual ADB command

            result = subprocess.run(full_command, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Command Failed: {e.stderr.strip() if e.stderr else 'Unknown Error'}")
            return ""

    def clear_facebook_data(self):
        """🔥 Fully clear Facebook data and spoof device identity with proper root access."""
        print(f"🔥 Clearing Facebook data on {self.device_id}...")

        # ✅ Step 1: Ensure ADB root mode is enabled
        adb_root_status = self.run_adb_command(["adb", "-s", self.device_id, "shell", "whoami"])
        if adb_root_status != "root":
            print("⚠️ Warning: Emulator may not have full root access. Trying alternative methods.")

        # ✅ Step 2: Force Stop & Remove Facebook Data
        print("🛑 Force stopping Facebook...")
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "am", "force-stop", "com.facebook.katana"])

        print("🧹 Clearing Facebook app data...")
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "pm", "clear", "com.facebook.katana"])  # Normal clear

        if adb_root_status == "root":
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "rm", "-rf", "/data/data/com.facebook.katana"], as_root=True)
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "rm", "-rf", "/sdcard/Android/data/com.facebook.katana"], as_root=True)

        # ✅ Step 3: Spoof Device Identity (Fixed Argument Error)
        print("🔄 Changing device identity...")
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "global", "device_name", "\"Samsung Galaxy S23\""])
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "global", "model", "\"SM-S911B\""])
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "global", "manufacturer", "\"samsung\""])
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "global", "brand", "\"samsung\""])

        if adb_root_status == "root":
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "secure", "android_id", "$(date +%s%N | md5sum | cut -c 1-16)"], as_root=True)

        # ✅ Step 4: Reset Google Advertising ID (GAID)
        print("🔄 Resetting Advertising ID...")
        if adb_root_status == "root":
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "rm", "-rf", "/data/data/com.google.android.gms/shared_prefs/adid_settings.xml"], as_root=True)
        
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "am", "broadcast", "-a", "com.google.android.gms.INITIALIZE"])
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "secure", "adb_enabled", "0"])
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "settings", "put", "secure", "adb_enabled", "1"])

        # ✅ Step 5: Spoof Network Identifiers (IMEI, MAC, Hostname) - Using Root Only If Available
        print("🔄 Spoofing network identifiers...")
        if adb_root_status == "root":
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "setprop", "ro.serialno", "$(date +%s%N | md5sum | cut -c 1-16)"], as_root=True)
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "setprop", "net.hostname", "android-$(date +%s%N | md5sum | cut -c 1-8)"], as_root=True)
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "setprop", "ro.boot.wifimac", "$(cat /sys/class/net/wlan0/address | sed 's/://g')"], as_root=True)
            self.run_adb_command(["adb", "-s", self.device_id, "shell", "setprop", "ro.boot.btmacaddr", "$(cat /sys/class/net/bt0/address | sed 's/://g')"], as_root=True)
        else:
            print("⚠️ Warning: Root commands skipped due to missing `su`.")

        # ✅ Step 6: Restart Facebook Instead of Emulator
        print("🔄 Restarting Facebook services...")
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "am", "force-stop", "com.facebook.katana"])
        self.run_adb_command(["adb", "-s", self.device_id, "shell", "am", "start", "-n", "com.facebook.katana/.LoginActivity"])

        print("✅ Facebook data cleared, identity spoofed, and app restarted successfully!")

    def find_vm_config_files(self,vms_path):
        """Find all vm_config.json files inside dynamically detected emulator folders."""
        config_files = []
        for folder in os.listdir(vms_path):
            folder_path = os.path.join(vms_path, folder, 'configs')
            config_file = os.path.join(folder_path, 'customer_config.json')
            if os.path.exists(config_file):
                config_files.append(config_file)
        return config_files

    def generate_random_imei(self):
        """Generate a random valid IMEI number using the Luhn algorithm."""
        imei_base = [random.randint(0, 9) for _ in range(14)]
        
        # Luhn algorithm checksum calculation
        checksum = 0
        for i, digit in enumerate(imei_base[::-1]):
            if i % 2 == 0:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digit
        
        imei_base.append((10 - (checksum % 10)) % 10)
        return "".join(map(str, imei_base))
    
    def change_imei(self):
        """Generate a new unique IMEI for each emulator and update their vm_config.json files."""
        config_files = self.find_vm_config_files(self.vms_path)
        
        if not config_files:
            messagebox.showerror("Error", "No emulator configurations found!")
            return
        
        imei_list = set()
        for file in config_files:
            new_imei = self.generate_random_imei()
            while new_imei in imei_list:  # Ensure each emulator gets a unique IMEI
                new_imei = self.generate_random_imei()
            imei_list.add(new_imei)
            
            # try:
            #     with open(file, 'r', encoding='utf-8') as f:
            #         config = json.load(f)
                
            #     if 'vm' in config and 'phone' in config['vm']:
            #         config['vm']['phone']['imei'] = new_imei
                    
            #         with open(file, 'w', encoding='utf-8') as f:
            #             json.dump(config, f, indent=2)
            # except Exception as e:
            #     messagebox.showerror("Error", f"Failed to update {file}: {str(e)}")
            #     return
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'setting' in config and 'phone' in config['setting']:
                    config['setting']['phone']['imei'] = new_imei
                    
                    with open(file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update {file}: {str(e)}")
                return
        messagebox.showinfo("Success", "IMEI updated successfully for all emulators! Restart MuMuPlayer to apply changes.")
