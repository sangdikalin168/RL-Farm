import os
import re
import time
import random
import string
import subprocess
from concurrent.futures import ThreadPoolExecutor
import cv2


class ADBController:
    """ADB Controller for automating Facebook registration on Android emulators."""
    ADB_PATH = r"C:\Users\MSI\Desktop\RL Farm\adb\adb.exe"
    def __init__(self, device_id):
        self.device_id = device_id
    
    def run_adb_command(self, command):
        """Runs an ADB command and returns the output."""
        try:
            full_command = [self.ADB_PATH, "-s", self.device_id] + command
            result = subprocess.run(full_command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Command Failed: {e.stderr.strip() if e.stderr else 'Unknown Error'}")
            return ""
    
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

    def open_facebook(self, lite=False):
        """Opens Facebook or Facebook Lite."""
        if lite:
            self.run_adb_command(["shell", "am", "start", "-n", "com.facebook.lite/com.facebook.lite.MainActivity"])
        else:
            self.run_adb_command(["shell", "am", "start", "-n", "com.facebook.katana/.LoginActivity"])
        time.sleep(5)

    def clear_facebook_data(self):
        """Clears Facebook app data to reset the registration flow."""
        print(f"🧹 Clearing Facebook data on {self.device_id}...")
        self.run_adb_command(["shell", "pm", "clear", "com.facebook.katana"])
        time.sleep(3)
    
    def take_screenshot(self, screenshot_path):
        """Takes a screenshot and saves it."""
        remote_path = "/sdcard/screen.png"
        self.run_adb_command(["shell", "screencap", "-p", remote_path])
        self.run_adb_command(["pull", remote_path, screenshot_path])
        self.run_adb_command(["shell", "rm", remote_path])

    def tap_img(self, template_path, max_attempts=10, delay=1, timeout=30):
        """🔥 Detects an image on the screen and taps it.

        Args:
            template_path (str): Path to the template image.
            max_attempts (int, optional): Maximum attempts to find the image. Defaults to 10.
            delay (int, optional): Delay between retries in seconds. Defaults to 1.
            timeout (int, optional): Maximum time allowed before stopping. Defaults to 30s.

        Returns:
            bool: True if the image is found and tapped, False otherwise.
        """
        screenshot_folder = "screenshots"
        os.makedirs(screenshot_folder, exist_ok=True)
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")
        
        start_time = time.time()  # ✅ Start timeout tracking
        
        # Remove existing screenshot if it exists
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        for attempt in range(max_attempts):
            # ✅ Step 1: Check timeout condition
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(f"⏳ Timeout reached ({timeout}s)! Stopping search.")
                return False

            # ✅ Step 2: Take a fresh screenshot
            self.take_screenshot(screenshot_path)

            # ✅ Step 3: Load images
            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

            if screenshot is None:
                print("❌ Failed to load the screenshot!")
                return False
            if template is None:
                print(f"❌ Template image not found at: {template_path}")
                return False

            # ✅ Step 4: Match template
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # ✅ Step 5: Check match confidence
            if max_val >= 0.8:
                h, w = template.shape[:2]
                center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2

                print(f"✅ Image detected! Tapping at ({center_x}, {center_y})...")
                self.tap(center_x, center_y)  # ✅ Perform tap action
                return True

            print(f"🔄 Attempt {attempt + 1}/{max_attempts}: Image not found, retrying in {delay}s...")
            time.sleep(delay)

        print("❌ Image not found after max attempts.")
        return False

    def tap_multiple_templates(self, template_paths, timeout=30, delay=1, match_actions=None):
        """🔥 Detects multiple templates on the screen and taps the first match.
        
        Args:
            template_paths (list): List of image paths to match.
            timeout (int, optional): Maximum wait time before stopping (seconds). Defaults to 30.
            delay (int, optional): Delay between retries in seconds. Defaults to 1.
            match_actions (dict, optional): Actions to execute when a specific template is matched.
                Example: {"templates/special_button.png": self.special_action_function}

        Returns:
            str: The matched template path if tapped, else None.
        """
        screenshot_folder = "screenshots"
        os.makedirs(screenshot_folder, exist_ok=True)
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', self.device_id)}.png")

        start_time = time.time()  # ✅ Start timeout tracking

        while time.time() - start_time < timeout:
            # ✅ Take a fresh screenshot
            self.take_screenshot(screenshot_path)

            # ✅ Load screenshot
            screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
            if screenshot is None:
                print("❌ Failed to load the screenshot!")
                return None

            for template_path in template_paths:
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    print(f"❌ Template not found: {template_path}")
                    continue

                # ✅ Match template
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= 0.8:
                    h, w = template.shape[:2]
                    center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2

                    print(f"✅ Detected {template_path}! Tapping at ({center_x}, {center_y})...")
                    self.tap(center_x, center_y)

                    # ✅ Execute custom action if defined
                    if match_actions and template_path in match_actions:
                        print(f"⚡ Executing custom action for {template_path}...")
                        match_actions[template_path]()

                    return template_path  # ✅ Return matched template

            print(f"🔄 Retrying... Waiting {delay}s")
            time.sleep(delay)

        print("⏳ Timeout! No template matched.")
        return None  # No match found

    def wait(self, seconds: float):
        """Waits for a specified amount of seconds."""
        time.sleep(seconds)

