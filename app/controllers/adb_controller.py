import os
import random
import re
import sys
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
import cv2
from pyzbar.pyzbar import decode
from urllib.parse import parse_qs, urlparse


class ADBController:
    """ADB Controller for automating Facebook registration on Android emulators."""

    def __init__(self, device_id):
        
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS  # Use _MEIPASS for PyInstaller EXE
        else:
            self.base_path = os.getcwd()
        
        self.device_id = device_id
        self.adb_path = os.path.join(self.base_path, "adb", "adb.exe")
        
        # Determine the path for screenshots. This should be consistent with EmulatorView.
        # It's better to put dynamic files (like screenshots) in a user's temp directory
        # or a known application data directory if they are meant to persist or be user-accessible.
        # For temporary files cleared by the app, sys._MEIPASS is acceptable.
        self.screenshots_dir = os.path.join(self.base_path, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True) # Ensure the directory exists

    def run_adb_command(self, command):
        """Runs an ADB command and returns the output."""
        try:
            full_command = [self.adb_path, "-s", self.device_id] + command
            result = subprocess.run(full_command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Command Failed: {e.stderr.strip() if e.stderr else 'Unknown Error'}")
            return ""
    
    def long_press(self, x, y, duration=2000):
        """Simulates a long press at (x, y) coordinates on the device."""
        self.run_adb_command(["shell", "input", "touchscreen", "swipe", str(x), str(y), str(x), str(y), str(duration)])
    
    def tap(self, x, y):
        """Simulates a tap at (x, y) coordinates on the device."""
        self.run_adb_command(["shell", "input", "tap", str(x), str(y)])

    def send_text(self, text):
        """Sends text input to the device."""
        if isinstance(text, tuple):
            # If it's a tuple, join the elements into a single string
            text = ' '.join(map(str, text))
        else:
            # Ensure it's a string
            text = str(text)
            
        escaped_text = text.replace(" ", "%s")
        self.run_adb_command(["shell", "input", "text", escaped_text])

    def open_app(self, package_name):
        """Open an app on the emulator by package name."""
        self.run_adb_command(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])

    def take_screenshot(self, screenshot_path):
        """Takes a screenshot and saves it."""
        remote_path = "/sdcard/screen.png"
        self.run_adb_command(["shell", "screencap", "-p", remote_path])
        self.run_adb_command(["pull", remote_path, screenshot_path])
        self.run_adb_command(["shell", "rm", remote_path])

    def detect_templates(self, template_paths, threshold=0.8, timeout=60, check_interval=1):
        """Continuously checks for templates until a match is found or timeout is reached."""
        # Use the pre-defined screenshots_dir from __init__
        screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            self.take_screenshot(screenshot_path)

            if not os.path.exists(screenshot_path) or os.path.getsize(screenshot_path) == 0:
                print("❌ Screenshot not found or empty.")
                return None
            
            screen = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            if screen is None:
                print("❌ Failed to load screenshot image. Check file integrity.")
                return None
            
            for original_template_path in template_paths: # template_paths now contains paths like "templates/my_template.png"
                # Construct the full, correct path to the template image
                template_adjusted_path = os.path.join(self.base_path, original_template_path)
                template_name = os.path.basename(original_template_path) # Use original for name display
                
                if not os.path.exists(template_adjusted_path):
                    print(f"⚠️ Template file not found: {template_adjusted_path}")
                    continue
                
                template = cv2.imread(template_adjusted_path, cv2.IMREAD_GRAYSCALE) # Use the adjusted path
                if template is None:
                    print(f"⚠️ Failed to load template image: {template_adjusted_path}")
                    continue
                
                result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                print(f"🔍 {template_name}: Match Confidence = {max_val:.4f}")
                
                if max_val >= threshold:
                    print(f"✅ Match found for {template_name}. Returning path.")
                    return original_template_path # Return the original path as passed in, not the adjusted internal path
                
            time.sleep(check_interval)    
        
        print("⏳ Timeout! No template matched within the wait time.")
        return "" # Or None, depending on expected return type for no match

    def tap_img(self, template_path, max_attempts=200, delay=1, timeout=60):
        """🔥 Detects an image on the screen and taps it.

        Args:
            template_path (str): Path to the template image (e.g., "templates/button.png").
            max_attempts (int, optional): Maximum attempts to find the image. Defaults to 10.
            delay (int, optional): Delay between retries in seconds. Defaults to 1.
            timeout (int, optional): Maximum time allowed before stopping. Defaults to 30s.

        Returns:
            bool: True if the image is found and tapped, False otherwise.
        """
        # Use the pre-defined screenshots_dir from __init__
        screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")
        
        start_time = time.time()
        
        # Remove existing screenshot if it exists
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        # Construct the full, correct path to the template image
        template_adjusted_path = os.path.join(self.base_path, template_path)
        
        for attempt in range(max_attempts):
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(f"⏳ Timeout reached ({timeout}s)! Stopping search.")
                return False

            self.take_screenshot(screenshot_path)

            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            template = cv2.imread(template_adjusted_path, cv2.IMREAD_GRAYSCALE) # Use the adjusted path

            if screenshot is None:
                print("❌ Failed to load the screenshot!")
                return False
            if template is None:
                print(f"❌ Template image not found at: {template_adjusted_path}") # Log the adjusted path
                return False

            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= 0.8:
                h, w = template.shape[:2]
                center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2

                print(f"✅ Image detected! Tapping at ({center_x}, {center_y})...") # You can re-enable this for more verbose logging
                self.tap(center_x, center_y)
                return True

            time.sleep(delay)

        print("❌ Image not found after max attempts.")
        return False

    def tap_imgs(self, template_paths, timeout=60, delay=1, match_actions=None):
        """🔥 Detects multiple templates on the screen and taps the first match.
        
        Args:
            template_paths (list): List of image paths to match (e.g., ["templates/img1.png", "templates/img2.png"]).
            timeout (int, optional): Maximum wait time before stopping (seconds). Defaults to 30.
            delay (int, optional): Delay between retries in seconds. Defaults to 1.
            match_actions (dict, optional): Actions to execute when a specific template is matched.
                Example: {"templates/special_button.png": self.special_action_function}

        Returns:
            str: The matched template path if tapped, else None.
        """
        # Use the pre-defined screenshots_dir from __init__
        screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")

        start_time = time.time()

        while time.time() - start_time < timeout:
            self.take_screenshot(screenshot_path)

            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            if screenshot is None:
                print("❌ Failed to load the screenshot!")
                return None

            for original_template_path in template_paths: # template_paths now contains paths like "templates/my_template.png"
                # Construct the full, correct path to the template image
                template_adjusted_path = os.path.join(self.base_path, original_template_path)
                
                template = cv2.imread(template_adjusted_path, cv2.IMREAD_GRAYSCALE) # Use the adjusted path
                if template is None:
                    print(f"❌ Template not found: {template_adjusted_path}") # Log the adjusted path
                    continue

                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= 0.8:
                    h, w = template.shape[:2]
                    center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2

                    print(f"✅ Detected {original_template_path}! Tapping at ({center_x}, {center_y})...")
                    self.tap(center_x, center_y)

                    if match_actions and original_template_path in match_actions:
                        print(f"⚡ Executing custom action for {original_template_path}...")
                        match_actions[original_template_path]()

                    return original_template_path # Return the original path as passed in

            # print(f"🔄 Retrying... Waiting {delay}s") # You can re-enable this for more verbose logging
            time.sleep(delay)

        print("⏳ Timeout! No template matched.")
        return None

    def wait_img(self, template_path, max_attempts=200, delay=1, timeout=60):
        """🔥 Waits for an image to appear on the screen.

        Args:
            template_path (str): Path to the template image (e.g., "templates/button.png").
            max_attempts (int, optional): Maximum attempts to find the image. Defaults to 10.
            delay (int, optional): Delay between retries in seconds. Defaults to 1.
            timeout (int, optional): Maximum time allowed before stopping. Defaults to 30s.
        
        Returns:
            bool: True if the image is found, False otherwise.
        """
        
        # Use the pre-defined screenshots_dir from __init__
        screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")

        start_time = time.time()
        # Construct the full, correct path to the template image
        template_adjusted_path = os.path.join(self.base_path, template_path)

        for attempt in range(max_attempts):
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(f"⏳ Timeout reached ({timeout}s)! Stopping search.")
                return False

            self.take_screenshot(screenshot_path)

            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            template = cv2.imread(template_adjusted_path, cv2.IMREAD_GRAYSCALE) # Use the adjusted path

            if screenshot is None:
                print("❌ Failed to load the screenshot!")
                return False
            if template is None:
                print(f"❌ Template image not found at: {template_adjusted_path}") # Log the adjusted path
                return False

            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val >= 0.8:
                # print(f"✅ Image detected after {attempt + 1} attempts!") # You can re-enable this for more verbose logging
                return True

            # print(f"🔄 Attempt {attempt + 1}/{max_attempts}: Image not found, retrying in {delay}s...") # You can re-enable this for more verbose logging
            time.sleep(delay)
            
        print("❌ Image not found after max attempts.")
        return False
    
    def wait_imgs(self, template_paths, timeout=60, delay=1):
        """🔥 Waits for multiple images to appear on the screen.

        Args:
            template_paths (list): List of image paths to match (e.g., ["templates/img1.png", "templates/img2.png"]).
            timeout (int, optional): Maximum wait time before stopping (seconds). Defaults to 30.
            delay (int, optional): Delay between retries in seconds. Defaults to 1.
            
        Returns:
            str: The matched template path if found, else None.
        """
        
        # Use the pre-defined screenshots_dir from __init__
        screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")

        start_time = time.time()
        while time.time() - start_time < timeout:
            self.take_screenshot(screenshot_path)

            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            if screenshot is None:
                print("❌ Failed to load the screenshot!")
                return None

            for original_template_path in template_paths: # template_paths now contains paths like "templates/my_template.png"
                # Construct the full, correct path to the template image
                template_adjusted_path = os.path.join(self.base_path, original_template_path)
                
                template = cv2.imread(template_adjusted_path, cv2.IMREAD_GRAYSCALE) # Use the adjusted path
                if template is None:
                    print(f"❌ Template not found: {template_adjusted_path}") # Log the adjusted path
                    continue

                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                if max_val >= 0.8:
                    print(f"✅ Detected {original_template_path} after {time.time() - start_time:.2f}s!")
                    return original_template_path # Return the original path as passed in

            # print(f"🔄 Retrying... Waiting {delay}s") # You can re-enable this for more verbose logging
            time.sleep(delay)
            
        print("⏳ Timeout! No template matched.")
        return None
    def wait(self, seconds: float):
        """Waits for a specified amount of seconds."""
        time.sleep(seconds)

    def swipe(self, start_x, start_y, end_x, end_y, duration=200):
        """Simulates a swipe gesture on the device."""
        self.run_adb_command(["shell", "input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration)])
        
    def randomize_device_fingerprint(self):
        # Generate random Android ID
        android_id = ''.join(random.choices('0123456789abcdef', k=16))
        print(f"📱 Setting Android ID: {android_id}")
        self.run_adb_command(["shell", "settings", "put", "secure", "android_id", android_id])

        # Random Timezone
        timezones = ["America/New_York", "Europe/London", "Asia/Tokyo", "Africa/Cairo"]
        tz = random.choice(timezones)
        print(f"🌍 Setting timezone: {tz}")
        self.run_adb_command(["shell", "setprop", "persist.sys.timezone", tz])

        # Random Locale
        locales = ["en-US"]
        locale = random.choice(locales)
        lang, country = locale.split("-")
        print(f"🌐 Setting locale: {locale}")
        self.run_adb_command(["shell", "setprop", "persist.sys.locale", locale])
        self.run_adb_command(["shell", "setprop", "persist.sys.language", lang])
        self.run_adb_command(["shell", "setprop", "persist.sys.country", country])

        # Clear WebView & Chrome
        print("🧹 Clearing WebView and Chrome...")
        self.run_adb_command(["shell", "pm", "clear", "com.google.android.webview"])
        self.run_adb_command(["shell", "pm", "clear", "com.android.chrome"])

        # Clear Play Services (to reset GAID)
        print("🔄 Clearing Google Play Services...")
        self.run_adb_command(["shell", "pm", "clear", "com.google.android.gms"])
        print("✅ Device fingerprint randomized.\n")       
        
    def clear_facebook_data(self):
        """🔥 Fully clear Facebook data and spoof device identity with proper root access."""
        print(f"🔥 Clearing Facebook data on {self.device_id}...")

        # ✅ Step 1: Ensure ADB root mode is enabled
        adb_root_status = self.run_adb_command(["-s", self.device_id, "shell", "whoami"])
        if adb_root_status != "root":
            print("⚠️ Warning: Emulator may not have full root access. Trying alternative methods.")

        # ✅ Step 2: Force Stop & Remove Facebook Data
        print("🛑 Force stopping Facebook...")
        self.run_adb_command(["-s", self.device_id, "shell", "am", "force-stop", "com.facebook.katana"])

        print("🧹 Clearing Facebook app data...")
        self.run_adb_command(["-s", self.device_id, "shell", "pm", "clear", "com.facebook.katana"])  # Normal clear

        # if adb_root_status == "root":
        #     self.run_adb_command(["-s", self.device_id, "shell", "rm", "-rf", "/data/data/com.facebook.katana"], as_root=True)
        #     self.run_adb_command(["-s", self.device_id, "shell", "rm", "-rf", "/sdcard/Android/data/com.facebook.katana"], as_root=True)

        # # ✅ Step 3: Spoof Device Identity (Fixed Argument Error)
        # print("🔄 Changing device identity...")
        # self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "global", "device_name", "\"Samsung Galaxy S23\""])
        # self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "global", "model", "\"SM-S911B\""])
        # self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "global", "manufacturer", "\"samsung\""])
        # self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "global", "brand", "\"samsung\""])

        # if adb_root_status == "root":
        #     self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "secure", "android_id", "$(date +%s%N | md5sum | cut -c 1-16)"], as_root=True)

        # # ✅ Step 4: Reset Google Advertising ID (GAID)
        # print("🔄 Resetting Advertising ID...")
        # if adb_root_status == "root":
        #     self.run_adb_command(["-s", self.device_id, "shell", "rm", "-rf", "/data/data/com.google.android.gms/shared_prefs/adid_settings.xml"], as_root=True)
        
        # self.run_adb_command(["-s", self.device_id, "shell", "am", "broadcast", "-a", "com.google.android.gms.INITIALIZE"])
        # self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "secure", "adb_enabled", "0"])
        # self.run_adb_command(["-s", self.device_id, "shell", "settings", "put", "secure", "adb_enabled", "1"])

        # # ✅ Step 5: Spoof Network Identifiers (IMEI, MAC, Hostname) - Using Root Only If Available
        # print("🔄 Spoofing network identifiers...")
        # if adb_root_status == "root":
        #     self.run_adb_command(["-s", self.device_id, "shell", "setprop", "ro.serialno", "$(date +%s%N | md5sum | cut -c 1-16)"], as_root=True)
        #     self.run_adb_command(["-s", self.device_id, "shell", "setprop", "net.hostname", "android-$(date +%s%N | md5sum | cut -c 1-8)"], as_root=True)
        #     self.run_adb_command(["-s", self.device_id, "shell", "setprop", "ro.boot.wifimac", "$(cat /sys/class/net/wlan0/address | sed 's/://g')"], as_root=True)
        #     self.run_adb_command(["-s", self.device_id, "shell", "setprop", "ro.boot.btmacaddr", "$(cat /sys/class/net/bt0/address | sed 's/://g')"], as_root=True)
        # else:
        #     print("⚠️ Warning: Root commands skipped due to missing `su`.")

        # # ✅ Step 6: Restart Facebook Instead of Emulator
        # print("🔄 Restarting Facebook services...")
        # self.run_adb_command(["-s", self.device_id, "shell", "am", "force-stop", "com.facebook.katana"])
        # self.run_adb_command(["-s", self.device_id, "shell", "am", "start", "-n", "com.facebook.katana/.LoginActivity"])

        print("✅ Facebook data cleared, identity spoofed, and app restarted successfully!")

    def extract_facebook_uid(self):
        # """Runs adb root, reads Facebook's auth XML, and extracts the UID."""
        # print("🚀 Running adb root...")
        # self.run_adb_command(["root"])

        # print("📄 Reading msys-auth-data.xml...")
        # xml_content = self.run_adb_command([
        #     "shell",
        #     "cat",
        #     "/data/data/com.facebook.katana/shared_prefs/msys-auth-data.xml"
        # ])

        # if not xml_content:
        #     print("❌ Failed to read XML or file does not exist.")
        #     return None

        # # Extract UID from the string name attribute
        # match = re.search(r'<string name="(\d+)-_rt_client_id"', xml_content)
        # if match:
        #     uid = match.group(1)
        #     print(f"✅ Extracted Facebook UID: {uid}")
        #     return uid
        # else:
        #     print("❌ UID not found in the XML.")
        #     return None
        
        """Extract Facebook UID from acra_criticaldata_store.xml on a rooted device."""
        print("🚀 Running adb root...")
        self.run_adb_command(["root"])

        print("📄 Reading acra_criticaldata_store.xml...")
        xml_content = self.run_adb_command([
            "shell",
            "cat",
            "/data/data/com.facebook.katana/shared_prefs/acra_criticaldata_store.xml"
        ])

        if not xml_content:
            print("❌ Failed to read XML or file does not exist.")
            return None

        # Match the USER_ID string value
        match = re.search(r'<string name="USER_ID">(\d+)</string>', xml_content)
        if match:
            uid = match.group(1)
            print(f"✅ Extracted Facebook UID: {uid}")
            return uid
        else:
            print("❌ USER_ID not found in the XML.")
            return None

    def extract_lite_uid(self):
        """Runs adb root, reads Facebook's auth XML, and extracts the UID."""
        print("🚀 Running adb root...")
        self.run_adb_command(["root"])

        print("📄 Reading msys-auth-data.xml...")
        xml_content = self.run_adb_command([
            "shell",
            "cat",
            "/data/data/com.facebook.lite/shared_prefs/msys-auth-data.xml"
        ])

        if not xml_content:
            print("❌ Failed to read XML or file does not exist.")
            return None

        # Extract UID from the string name attribute
        match = re.search(r'<string name="(\d+)-_rt_client_id"', xml_content)
        if match:
            uid = match.group(1)
            print(f"✅ Extracted Facebook UID: {uid}")
            return uid
        else:
            print("❌ UID not found in the XML.")
            return None
    
    def image_to_2fa(self):
        """Extracts 2FA code from the screenshot of the Facebook app."""
        screenshot_folder = "screenshots"
        os.makedirs(screenshot_folder, exist_ok=True)
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")
        
        # ✅ Take a fresh screenshot
        self.take_screenshot(screenshot_path)
        
        image = cv2.imread(screenshot_path)
        
        # Decode the QR code(s)
        decoded_objects = decode(image)
        
                # Process and print the results
        if decoded_objects:
            for obj in decoded_objects:
                # print("QR Code Data:", obj.data.decode('utf-8'))
                # print("QR Code Type:", obj.type)
                # Parse the URI
                parsed = urlparse(obj.data.decode('utf-8'))
                # Extract key components
                scheme = parsed.scheme  # otpauth
                path = parsed.path.split(":")  # Split the identifier
                query = parse_qs(parsed.query)  # Parse query parameters
                secret = query.get("secret", [""])[0]
                formatted_secret = ' '.join(secret[i:i+4] for i in range(0, len(secret), 4))
            return formatted_secret
        else:
            print("No QR code detected.")
