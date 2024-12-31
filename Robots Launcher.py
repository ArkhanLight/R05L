import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt
import struct
import subprocess
import os
import webbrowser

class RobotsLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robots Launcher")
        self.setFixedSize(440, 280)

        # Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 20px;
                border-radius: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-size: 14px;
            }
            QCheckBox {
                color: white;
                padding: 5px;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #2d2d2d;
                border: 1px solid #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #005f99;
            }
            QLabel {
                font-size: 14px;
            }
            QLabel#speedrunLabel {
                font-size: 10px;
                color: #aaaaaa;
            }
        """)

        # Main Layout
        main_layout = QVBoxLayout()

        # Fullscreen Checkbox
        fullscreen_layout = QHBoxLayout()
        self.fullscreen_checkbox = QCheckBox("Windowed")
        fullscreen_layout.addWidget(self.fullscreen_checkbox)
        fullscreen_layout.addStretch()
        main_layout.addLayout(fullscreen_layout)

        # Resolution Section
        res_section_layout = QVBoxLayout()
        res_section_layout.setSpacing(5)  # Spacing inside the resolution section

        # Horizontal layout for label and dropdown
        res_layout = QHBoxLayout()
        res_label = QLabel("Select Resolution:")
        res_layout.addWidget(res_label)

        self.res_dropdown = QComboBox()
        self.res_dropdown.addItems([
            "640x480 *", "800x600 *", "1024x768 *", "1280x960 *", "1280x720", "1366x768", "1600x900", "1920x1080", "2560×1440", "3840x2160", "7680x4320"
        ])
        res_layout.addWidget(self.res_dropdown)
        res_section_layout.addLayout(res_layout)

        # Small text directly below the label and dropdown
        speedrun_label = QLabel("Only resolutions marked with a * are acceptable for speedrun submissions.")
        speedrun_label.setObjectName("speedrunLabel")
        speedrun_label.setAlignment(Qt.AlignLeft)  # Ensure left alignment
        res_section_layout.addWidget(speedrun_label)

        # Add the resolution section to the main layout
        main_layout.addLayout(res_section_layout)

        # Starting Level Section
        level_section_layout = QVBoxLayout()
        level_layout = QHBoxLayout()
        level_label = QLabel("Starting Level:")
        level_layout.addWidget(level_label)

        self.level_dropdown = QComboBox()
        self.level_dropdown.addItems([
            "Main Menu", "Rivet Town", "City Journey", "The City", "Bigweld's Factory",
            "Outmode Zone", "City Raceways", "The Old Sewer", "Sewer Showdown", "Bigweld's Mansion",
            "Bigweld's Chase", "The Chopshop", "Ratchet Showdown", "DEV MAP - Mechanics", "DEV MAP - Enemies", "DEV MAP - NPC's",
            "DEV MAP - Ball", "DEV MAP - Empty Aunt Fanny's House"
        ])
        level_layout.addWidget(self.level_dropdown)
        level_section_layout.addLayout(level_layout)

        # Remove Intro Screen Checkbox
        self.remove_intro_checkbox = QCheckBox("Remove Robots Splash Screen")
        level_section_layout.addWidget(self.remove_intro_checkbox)

        # Add the starting level section to the main layout
        main_layout.addLayout(level_section_layout)

        # Add spacing between starting level and buttons
        main_layout.addSpacing(27)

        # Buttons Section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Adjust spacing between buttons

        self.speedrun_button = QPushButton("Visit Speedrun Page")
        self.speedrun_button.setObjectName("secondary")
        self.speedrun_button.clicked.connect(self.open_speedrun_page)
        buttons_layout.addWidget(self.speedrun_button)

        self.launch_button = QPushButton("Save and Launch Game")
        self.launch_button.clicked.connect(self.launch_game)
        buttons_layout.addWidget(self.launch_button)

        # Center the buttons layout in the main layout
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Connect level dropdown to splash screen checkbox
        self.level_dropdown.currentTextChanged.connect(self.update_intro_checkbox_state)
        
        # Connect the remove intro checkbox to its handler
        self.remove_intro_checkbox.stateChanged.connect(self.on_intro_checkbox_toggled)

        # Check the version of the executable
        self.check_exe_version("Robots.exe")  # Moved here after defining the checkbox

        self.init_settings()
        
    def detect_and_update_version(self, exe_path):
        if hasattr(self, "_exe_checked") and self._exe_checked:
            return  # Prevent multiple executions
        self._exe_checked = True  # Mark as checked

        if not os.path.exists(exe_path):
            QMessageBox.warning(self, "Error", f"{exe_path} not found!")
            self.update_level_dropdown(is_us_version=False)  # Default to EU
            return

        try:
            with open(exe_path, "rb") as f:
                header = f.read(64)
            detected_bytes = header[60:62]
            detected_hex = detected_bytes.hex().upper()
            print(f"Detected bytes: {detected_hex}")

            if detected_bytes == b'\x8C\x00':  # US version
                QMessageBox.information(self, "Version Detected", "US version detected.")
                self.update_level_dropdown(is_us_version=True)
            elif detected_bytes == b'\x20\x09':  # EU version
                QMessageBox.information(self, "Version Detected", "EU version detected.\n\nNote: the Robots splash screen removal feature together with the DEV maps are only available in the US version.")
                self.update_level_dropdown(is_us_version=False)
            else:
                QMessageBox.warning(
                    self,
                    "Unknown Version",
                    f"Unknown version detected: {detected_hex}. Please contact ArkhanLight on Discord about this unknown version.",
                )
                self.update_level_dropdown(is_us_version=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read the executable: {e}")
            self.update_level_dropdown(is_us_version=False)

    def is_us_version(self):
        exe_path = "Robots.exe"
        try:
            with open(exe_path, "rb") as f:
                header = f.read(64)
            detected_bytes = header[60:62]
            return detected_bytes == b'\x8C\x00'  # US version byte pattern
        except Exception:
            return False

    def check_exe_version(self, exe_path):
        if hasattr(self, "_exe_checked") and self._exe_checked:
            return  # Prevent multiple calls
        self._exe_checked = True  # Set the flag after the first execution

        if not os.path.exists(exe_path):
            QMessageBox.warning(self, "Error", f"{exe_path} not found!")
            self.update_level_dropdown(is_us_version=False)  # Default to EU
            return False  # Indicate failure

        try:
            with open(exe_path, "rb") as f:
                # Read the first 64 bytes
                header = f.read(64)

            detected_bytes = header[60:62]

            # Debugging: Print the specific bytes to verify
            detected_hex = detected_bytes.hex().upper()
            print(f"Detected bytes: {detected_hex}")

            # Check for US or EU version based on specific bytes
            if detected_bytes == b'\x8C\x00':  # US version
                QMessageBox.information(self, "Version Detected", "US version detected.")
                self.update_level_dropdown(is_us_version=True)  # Include DEV MAPS
            elif detected_bytes == b'\x20\x09':  # EU version
                QMessageBox.information(self, "Version Detected", "EU version detected.\n\nNote: the Robots splash screen removal feature together with the DEV maps are only available in the US version.")
                self.update_level_dropdown(is_us_version=False)  # Exclude DEV MAPS
            else:
                QMessageBox.warning(
                    self,
                    "Unknown Version",
                    f"Unknown version detected: {detected_hex}. The Launcher might still work though. Please contact ArkhanLight on Discord about this unknown version of the game.",
                )
                self.update_level_dropdown(is_us_version=False)  # Default to EU

            return True  # Indicate success
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read the executable: {e}")
            self.update_level_dropdown(is_us_version=False)  # Default to EU
            return False  # Indicate failure

    def update_intro_checkbox_state(self):
        exe_path = "Robots.exe"

        # Handle the state for the "Main Menu" level
        if self.level_dropdown.currentText() == "Main Menu":
            self.remove_intro_checkbox.setEnabled(False)
            self.remove_intro_checkbox.setChecked(False)
            self.remove_intro_checkbox.setStyleSheet("""
                QCheckBox {
                    color: #4d4d4d;
                }
                QCheckBox::indicator {
                    background-color: #4d4d4d;
                    border: 1px solid #4d4d4d;
                }
                QCheckBox::indicator:checked {
                    background-color: #4d4d4d;
                    border: 1px solid #4d4d4d;
                }
            """)

            # Restore splash screen bytes if the exe exists
            if os.path.exists(exe_path):
                self.restore_splash_screen_bytes(exe_path)
            return

        # Reset the checkbox state based on the detected version
        try:
            with open(exe_path, "rb") as f:
                header = f.read(64)
            detected_bytes = header[60:62]

            if detected_bytes == b'\x8C\x00':  # US version
                self.remove_intro_checkbox.setEnabled(True)
                self.remove_intro_checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #ffffff;
                    }
                    QCheckBox::indicator {
                        background-color: #2d2d2d;
                        border: 1px solid #ffffff;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #007acc;
                        border: 1px solid #005f99;
                    }
                """)
            elif detected_bytes == b'\x20\x09':  # EU version
                self.remove_intro_checkbox.setEnabled(False)
                self.remove_intro_checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #4d4d4d;
                    }
                    QCheckBox::indicator {
                        background-color: #4d4d4d;
                        border: 1px solid #4d4d4d;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #4d4d4d;
                        border: 1px solid #4d4d4d;
                    }
                """)
            else:  # Unknown version
                self.remove_intro_checkbox.setEnabled(True)
                self.remove_intro_checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #ffffff;
                    }
                    QCheckBox::indicator {
                        background-color: #2d2d2d;
                        border: 1px solid #ffffff;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #007acc;
                        border: 1px solid #005f99;
                    }
                """)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update intro checkbox state: {e}")

    def update_level_dropdown(self, is_us_version):
        base_levels = [
            "Main Menu", "Rivet Town", "City Journey", "The City", "Bigweld's Factory",
            "Outmode Zone", "City Raceways", "The Old Sewer", "Sewer Showdown", "Bigweld's Mansion",
            "Bigweld's Chase", "The Chopshop", "Ratchet Showdown"
        ]
        dev_maps = ["DEV MAP - Mechanics", "DEV MAP - Enemies", "DEV MAP - NPC's", "DEV MAP - Ball", "DEV MAP - Empty Aunt Fanny's House"]

        self.level_dropdown.clear()  # Clear the dropdown first

        if is_us_version:
            print("Updating levels for US version")  # Debugging output
            self.level_dropdown.addItems(base_levels + dev_maps)
        else:
            print("Updating levels for EU version")  # Debugging output
            self.level_dropdown.addItems(base_levels)


    def restore_splash_screen_bytes(self, file_path):
        try:
            with open(file_path, "rb") as f:
                data = bytearray(f.read())

            # Find the pattern for the splash screen
            pattern = b'\x0B\x99\x5D\x00\x64\xA1'
            pos = data.find(pattern)
            if pos == -1:
                # QMessageBox.warning(self, "Error", "Splash screen pattern not found.")
                return

            # Calculate the position of the bytes to restore
            splash_patch_offset = pos - 3
            if splash_patch_offset < 0 or splash_patch_offset + 3 > len(data):
                QMessageBox.warning(self, "Error", "Splash screen bytes out of range.")
                return

            # Restore the bytes to play the splash screen
            data[splash_patch_offset:splash_patch_offset + 3] = b'\x6A\xFF\x68'

            # Write the restored data back to the file
            with open(file_path, "wb") as f:
                f.write(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore splash screen bytes: {e}. Please close your process of Robots before opening the launcher.")

    def on_intro_checkbox_toggled(self):
        exe_path = "Robots.exe"
        if os.path.exists(exe_path):
            self.remove_intro_screen(exe_path)

    def init_settings(self):
        exe_path = "Robots.exe"

        # Ensure the version is detected and dropdown updated
        self.detect_and_update_version(exe_path)

        # Read and set the resolution
        current_resolution = self.read_current_resolution(exe_path)
        if current_resolution and current_resolution in [self.res_dropdown.itemText(i) for i in range(self.res_dropdown.count())]:
            self.res_dropdown.setCurrentText(current_resolution)
        else:
            self.res_dropdown.setCurrentIndex(0)  # Default to the first item if no match

        # Read and set the windowed setting
        windowed_setting = self.read_windowed_setting("dgVoodoo.conf")
        self.fullscreen_checkbox.setChecked(windowed_setting)

        # Read and set the starting level
        current_starting_level = self.read_current_starting_level(exe_path)
        if current_starting_level:
            self.level_dropdown.setCurrentText(current_starting_level)

        # Check the intro screen status
        intro_screen_removed = self.check_intro_screen_status(exe_path)

        # Enable/disable the checkbox based on the game version
        if self.is_us_version():
            self.remove_intro_checkbox.setEnabled(True)
            self.remove_intro_checkbox.setChecked(intro_screen_removed)
        else:
            self.remove_intro_checkbox.setEnabled(False)
            self.remove_intro_checkbox.setChecked(False)

        # Update the checkbox state based on the starting level
        self.update_intro_checkbox_state()

    def check_intro_screen_status(self, file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()

            # Locate the pattern for the splash screen
            pattern = b'\x0B\x99\x5D\x00\x64\xA1'
            pos = data.find(pattern)
            if pos == -1:
                return False  # Pattern not found; assume splash screen is not removed

            # Check the state of the preceding bytes
            intro_patch_offset = pos - 3
            if intro_patch_offset < 0 or intro_patch_offset + 3 > len(data):
                return False  # Out of range; assume splash screen is not removed

            # Check if the patch bytes are present
            patched_bytes = b'\xB0\x01\xC3'
            original_bytes = b'\x6A\xFF\x68'

            # Return True if patched, False otherwise
            return data[intro_patch_offset:intro_patch_offset + 3] == patched_bytes
        except Exception as e:
            print(f"Error in check_intro_screen_status: {e}")
            return False

    def read_current_resolution(self, file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()

            # Find the resolution pattern
            pattern = b'\x66\xC7\x40\x02'
            positions = []
            pos = data.find(pattern)
            while pos != -1:
                positions.append(pos)
                pos = data.find(pattern, pos + 1)

            if len(positions) < 3:
                return None

            # Get the width and height
            target_pos = positions[2]  # Typically the 3rd occurrence
            width_pos = target_pos - 2
            height_pos = target_pos + 4

            width = int.from_bytes(data[width_pos:width_pos + 2], byteorder="little")
            height = int.from_bytes(data[height_pos:height_pos + 2], byteorder="little")

            # Create a resolution string
            resolution = f"{width}x{height}"

            # Append `*` if the resolution is 4:3
            if width / height == 4 / 3:
                resolution += " *"

            return resolution
        except Exception as e:
            print(f"Error in read_current_resolution: {e}")
            return None
            
    def read_current_starting_level(self, file_path):
        try:
            level_map = {
                0x0d: "Main Menu",
                0x12: "Rivet Town",
                0x1d: "City Journey",
                0x71: "The City",
                0x15: "Bigweld's Factory",
                0x50: "Outmode Zone",
                0x72: "City Raceways",
                0x53: "The Old Sewer",
                0x73: "Sewer Showdown",
                0x6e: "Bigweld's Mansion",
                0x6f: "Bigweld's Chase",
                0x1a: "The Chopshop",
                0xbb: "Ratchet Showdown",
                0x37: "DEV MAP - Mechanics",
                0x0f: "DEV MAP - Enemies",
                0xa0: "DEV MAP - NPC's",
                0x74: "DEV MAP - Ball",
                0x01: "DEV MAP - Empty Aunt Fanny's House"
            }

            with open(file_path, "rb") as f:
                data = f.read()

            # Locate the pattern that identifies the starting level
            pattern = b'\x00\x00\xC7\x86\x18\x03\x00\x00'
            pos = data.find(pattern)
            if pos == -1:
                return None

            # Extract the byte that represents the starting level
            level_offset = pos + len(pattern)
            current_level_byte = data[level_offset]

            # Return the level name if it exists in the map
            return level_map.get(current_level_byte, None)
        except Exception:
            QMessageBox.warning(self, "Warning", "Failed to read current starting level from Robots.exe.")
            return None


    def read_windowed_setting(self, conf_path):
        try:
            with open(conf_path, "r") as conf_file:
                for line in conf_file:
                    if "FullScreenMode" in line:
                        return "false" in line.lower()
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", f"{conf_path} not found!")
        return True

    def modify_windowed_setting(self, conf_path, windowed_enabled):
        try:
            lines = []
            with open(conf_path, "r") as conf_file:
                lines = conf_file.readlines()

            with open(conf_path, "w") as conf_file:
                for line in lines:
                    if "FullScreenMode" in line:
                        conf_file.write(f"FullScreenMode = {'false' if windowed_enabled else 'true'}\n")
                    else:
                        conf_file.write(line)
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", f"{conf_path} not found!")

    def modify_resolution(self, file_path, width, height):
        try:
            with open(file_path, "rb") as f:
                data = bytearray(f.read())

            pattern = b'\x66\xC7\x40\x02'
            positions = []
            pos = data.find(pattern)
            while pos != -1:
                positions.append(pos)
                pos = data.find(pattern, pos + 1)

            if len(positions) < 3:
                QMessageBox.warning(self, "Error", "Pattern not found or insufficient occurrences for resolution modification!")
                return False

            target_pos = positions[2]  # Typically the 3rd occurrence
            width_pos = target_pos - 2
            height_pos = target_pos + 4

            if width_pos < 0 or height_pos + 2 > len(data):
                QMessageBox.warning(self, "Error", "Resolution patch offset is out of range.")
                return False

            # Modify width and height
            data[width_pos:width_pos + 2] = struct.pack("<H", width)
            data[height_pos:height_pos + 2] = struct.pack("<H", height)

            # Write the modified data back to the file
            with open(file_path, "wb") as f:
                f.write(data)

            return True
        except PermissionError:
            QMessageBox.critical(self, "Error", f"Permission denied: {file_path}. Please close your current process of Robots or run the launcher as Administrator.")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to modify resolution: {e}")
            return False

    def modify_starting_level(self, file_path, level):
        try:
            level_map = {
                "Main Menu": 0x0d,
                "Rivet Town": 0x12,
                "City Journey": 0x1d,
                "The City": 0x71,
                "Bigweld's Factory": 0x15,
                "Outmode Zone": 0x50,
                "City Raceways": 0x72,
                "The Old Sewer": 0x53,
                "Sewer Showdown": 0x73,
                "Bigweld's Mansion": 0x6e,
                "Bigweld's Chase": 0x6f,
                "The Chopshop": 0x1a,
                "Ratchet Showdown": 0xbb,
                "DEV MAP - Mechanics": 0x37,
                "DEV MAP - Enemies": 0x0f,
                "DEV MAP - NPC's": 0xa0,
                "DEV MAP - Ball": 0x74,
                "DEV MAP - Empty Aunt Fanny's House": 0x01
            }

            with open(file_path, "rb") as f:
                data = bytearray(f.read())

            pattern = b'\x00\x00\xC7\x86\x18\x03\x00\x00'
            level_pos = data.find(pattern)
            if level_pos == -1:
                QMessageBox.warning(self, "Warning", "Starting level pattern not found! Contact ArkhanLight on Discord.")
                return

            level_offset = level_pos + len(pattern)
            data[level_offset] = level_map[level]

            with open(file_path, "wb") as f:
                f.write(data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to modify starting level: {e}. Contact ArkhanLight on Discord.")

    def remove_intro_screen(self, file_path):
        try:
            with open(file_path, "rb") as f:
                data = bytearray(f.read())

            # Locate the pattern for the splash screen
            pattern = b'\x0B\x99\x5D\x00\x64\xA1'
            pos = data.find(pattern)
            if pos == -1:
                QMessageBox.warning(self, "Error", "Splash screen pattern not found. Cannot patch.")
                return False

            # Calculate the start of the patchable section
            intro_patch_offset = pos - 3
            if intro_patch_offset < 0 or intro_patch_offset + 3 > len(data):
                QMessageBox.warning(self, "Error", "Splash screen patch offset is out of range.")
                return False

            # Modify the bytes based on the checkbox state
            if self.remove_intro_checkbox.isChecked():
                # Patch the splash screen bytes
                data[intro_patch_offset:intro_patch_offset + 3] = b'\xB0\x01\xC3'
            else:
                # Restore the original splash screen bytes
                data[intro_patch_offset:intro_patch_offset + 3] = b'\x6A\xFF\x68'

            # Save changes back to the file
            with open(file_path, "wb") as f:
                f.write(data)

            return True
        except PermissionError:
            QMessageBox.critical(self, "Error", f"Permission denied: {file_path}. Please close your current process of Robots or run the launcher as Administrator.")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to modify intro screen bytes: {e}")
            return False

    def launch_game(self):
        selected_res = self.res_dropdown.currentText().replace("*", "").strip()
        if not selected_res:
            QMessageBox.warning(self, "Warning", "Please select a resolution!")
            return

        selected_level = self.level_dropdown.currentText()

        width, height = map(int, selected_res.split('x'))
        exe_path = "Robots.exe"
        conf_path = "dgVoodoo.conf"

        if not os.path.exists(exe_path):
            QMessageBox.critical(self, "Error", f"{exe_path} not found! Contact ArkhanLight on Discord.")
            return

        # Modify windowed setting
        self.modify_windowed_setting(conf_path, self.fullscreen_checkbox.isChecked())

        # Apply/remove intro screen patch only if the checkbox is checked
        if self.remove_intro_checkbox.isChecked():
            if not self.remove_intro_screen(exe_path):
                return  # Stop if patch fails

        # Modify resolution and starting level
        if self.modify_resolution(exe_path, width, height):
            self.modify_starting_level(exe_path, selected_level)
            try:
                subprocess.Popen([exe_path]).wait()
            except Exception:
                QMessageBox.critical(self, "Error", "Failed to launch the game! Contact ArkhanLight on Discord.")



    def open_speedrun_page(self):
        webbrowser.open("https://www.speedrun.com/robots2005")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = RobotsLauncher()
    launcher.show()
    sys.exit(app.exec_())
