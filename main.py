import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import subprocess
import webbrowser

class ApexResolutionSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Apex Legends Configuration Switcher")

        # Resolution options
        resolutions = [("1920x1080", "1920", "1080"),
                       ("1728x1080", "1728", "1080"),
                       ("1440x1080", "1440", "1080"),
                       # Add more resolutions as needed
                       ]

        # Create resolution selection dropdown
        self.resolution_var = tk.StringVar()
        self.resolution_var.set(resolutions[0][0])  # Default resolution
        resolution_label = ttk.Label(root, text="Select Resolution:")
        resolution_label.grid(row=0, column=0, padx=10, pady=10)
        resolution_dropdown = ttk.Combobox(root, textvariable=self.resolution_var, values=[res[0] for res in resolutions])
        resolution_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Checkbox for autoexec.cfg
        self.autoexec_var = tk.BooleanVar()
        autoexec_checkbox = ttk.Checkbutton(root, text="Include autoexec.cfg", variable=self.autoexec_var)
        autoexec_checkbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        # Checkbox for fps limit
        self.fps_limit_var = tk.BooleanVar()
        fps_limit_checkbox = ttk.Checkbutton(root, text="Limit fps", variable=self.fps_limit_var, command=self.toggle_fps_limit)
        fps_limit_checkbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        # Entry for specifying fps limit
        self.fps_limit_entry = ttk.Entry(root, state=tk.DISABLED)
        self.fps_limit_entry.grid(row=2, column=1, padx=10, pady=5)

        # Checkbox for skip intro scene
        self.skip_intro_var = tk.BooleanVar()
        skip_intro_checkbox = ttk.Checkbutton(root, text="Skip intro scene (novid)", variable=self.skip_intro_var)
        skip_intro_checkbox.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        # Button to apply selected configuration
        apply_button = ttk.Button(root, text="Apply Configuration", command=self.apply_configuration)
        apply_button.grid(row=4, column=0, columnspan=2, pady=10)

    def toggle_fps_limit(self):
        # Enable/Disable fps_limit_entry based on fps_limit_var
        if self.fps_limit_var.get():
            self.fps_limit_entry.config(state=tk.NORMAL)
        else:
            self.fps_limit_entry.config(state=tk.DISABLED)

    def find_steam_exe(self):
        try:
            # Common installation path on Windows
            common_path = os.path.join(os.getenv("ProgramFiles(x86)"), "Steam", "steam.exe")

            # Check if Steam executable exists in common path
            if os.path.isfile(common_path):
                print(f"Steam executable found: {common_path}")
                return common_path
            else:
                print(f"Steam executable not found in common path: {common_path}")

            # Iterate over common drive letters and check for Steam executable
            for drive_letter in ["C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]:
                drive_path = os.path.join(f"{drive_letter}:", "Program Files (x86)", "Steam", "steam.exe")
                if os.path.isfile(drive_path):
                    print(f"Steam executable found on drive {drive_letter}: {drive_path}")
                    return drive_path

            # If not found, ask the user to manually select the Steam executable
            steam_exe_path = filedialog.askopenfilename(title="Select Steam Executable", filetypes=[("Executable files", "*.exe")])

            if steam_exe_path and os.path.isfile(steam_exe_path):
                print(f"Steam executable selected: {steam_exe_path}")
                return steam_exe_path
            else:
                print("Steam executable not selected.")
                return None
        except Exception as e:
            print(f"Error finding Steam executable: {e}")
            return None

    def apply_configuration(self):
        resolution = self.resolution_var.get().split('x')
        width, height = int(resolution[0]), int(resolution[1])

        # Path to the settings file
        settings_path = os.path.join(os.path.expanduser('~'), 'Saved Games', 'Respawn', 'Apex', 'local', 'videoconfig.txt')

        # Remove read-only attribute before writing
        self.set_read_only(settings_path, read_only=False)

        # Read the contents of the file
        with open(settings_path, 'r') as file:
            lines = file.readlines()

        # Find the index of "setting.defaultres" in lines
        defaultres_index = next((i for i, line in enumerate(lines) if 'setting.defaultres' in line), -1)
        defaultresheight_index = next((i for i, line in enumerate(lines) if 'setting.defaultresheight' in line), -1)

        # Update the resolution strings
        if defaultres_index != -1 and defaultresheight_index != -1:
            lines[defaultres_index] = f'\t"setting.defaultres"\t\t"{width}"\n'
            lines[defaultresheight_index] = f'\t"setting.defaultresheight"\t\t"{height}"\n'

        # Write the updated contents back to the file
        with open(settings_path, 'w') as file:
            file.writelines(lines)

        print(f"Resolution set to {width}x{height}")

        # Set the videoconfig.txt file as read-only
        self.set_read_only(settings_path)

        # Print the contents of the file for debugging
        print("Updated videoconfig.txt contents:")
        print("".join(lines))

        # Generate command line arguments based on checkboxes
        command_line_args = []
        if self.autoexec_var.get():
            command_line_args.append("+exec autoexec")
        if self.fps_limit_var.get():
            fps_limit_value = self.fps_limit_entry.get()
            if fps_limit_value.isdigit():
                command_line_args.append(f"+fps_max {fps_limit_value}")
            else:
                messagebox.showerror("Error", "Invalid FPS limit value. Please enter a valid number.")
                return
        if self.skip_intro_var.get():
            command_line_args.append("-novid")

        # Execute the game with the generated command line arguments
        steam_exe_path = self.find_steam_exe()
        if steam_exe_path:
            self.execute_game(command_line_args, steam_exe_path)
        else:
            print("Steam executable not found.")

    def set_read_only(self, file_path, read_only=True):
        try:
            if read_only:
                os.chmod(file_path, 0o444)  # Set the file as read-only
                print(f"{file_path} set as read-only.")
            else:
                os.chmod(file_path, 0o644)  # Set the file with read and write permissions
                print(f"{file_path} set with read and write permissions.")
        except Exception as e:
            print(f"Error setting {file_path} permissions: {e}")

    def execute_game(self, command_line_args, steam_exe_path):
        # Retrieve existing command line arguments
        existing_arguments = ' '.join(sys.argv[1:])

        # Combine existing and new launch options
        combined_options = f'{existing_arguments} {" ".join(command_line_args)}'

        print(f"Generated command line arguments: {combined_options}")

        try:
            # Use Steam protocol URL to launch the game
            steam_url = f'steam://run/1172470//{combined_options}'
            webbrowser.open(steam_url)
            print("Game launched successfully.")
        except Exception as e:
            print(f"Error launching the game: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ApexResolutionSwitcher(root)
    root.mainloop()
