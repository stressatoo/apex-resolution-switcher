import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess

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

        # Update the resolution strings
        for i in range(len(lines)):
            if 'setting.defaultres' in lines[i]:
                lines[i] = f'"setting.defaultres"\t\t"{width}"\n'
            elif 'setting.defaultresheight' in lines[i]:
                lines[i] = f'"setting.defaultresheight"\t\t"{height}"\n'

        # Write the updated contents back to the file
        with open(settings_path, 'w') as file:
            file.writelines(lines)

        print(f"Resolution set to {width}x{height}")

        # Set the videoconfig.txt file as read-only
        self.set_read_only(settings_path)

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
        self.execute_game(command_line_args)

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

    def execute_game(self, command_line_args):
        # Retrieve existing command line arguments
        existing_arguments = ' '.join(sys.argv[1:])

        # Combine existing and new launch options
        combined_options = f'{existing_arguments} {" ".join(command_line_args)}'

        # Uncomment the following line if you want to add Steam launch options
        self.add_steam_launch_options(combined_options)

        print(f"Game launched with command line arguments: {combined_options}")

    def add_steam_launch_options(self, combined_options):
        steam_exe = r'C:\Program Files (x86)\Steam\Steam.exe'  # Update this path with your Steam installation
        game_id = '1172470'  # Apex Legends game ID on Steam
        
        try:
            subprocess.run([steam_exe, f'–applaunch {game_id} {combined_options}'])
            print("Steam launch options updated.")
        except Exception as e:
            print(f"Error updating Steam launch options: {e}")
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ApexResolutionSwitcher(root)
    root.mainloop()
