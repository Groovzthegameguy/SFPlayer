import os
import xml.etree.ElementTree as ET
import tkinter as tk
from PIL import Image, ImageTk
import subprocess

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SFPlayer")
        self.geometry("800x600")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.icon_frame = tk.Frame(self.main_frame)
        self.icon_frame.pack(side="left", anchor="nw", padx=10, pady=10, fill="both", expand=True)

        self.icon_width = 100
        self.icon_height = 150
        self.spacing = 10

        self.search_games_directory()

    def search_games_directory(self):
        games_directory = "Games"

        if os.path.exists(games_directory) and os.path.isdir(games_directory):
            folders = [name for name in os.listdir(games_directory)
                       if os.path.isdir(os.path.join(games_directory, name))]

            if folders:
                print(f"Found the following folders in '{games_directory}':")
                for folder in folders:
                    title_file = os.path.join(games_directory, folder, "title.xml")
                    if os.path.exists(title_file):
                        game_name = self.extract_game_name(title_file)
                        bmp_file = os.path.join(games_directory, folder, "TitleLogo_n.bmp")
                        self.create_icon(game_name, bmp_file, folder)
                    else:
                        print(f"- {folder} (No title.xml found)")
            else:
                print(f"No folders were found in the '{games_directory}' directory.")
        else:
            print(f"The directory '{games_directory}' does not exist.")

    def extract_game_name(self, xml_file):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            name_element = root.find(".//name")
            if name_element is not None:
                return name_element.text
            else:
                return "Unknown Name"
        except ET.ParseError:
            return "Error Parsing XML"

    def create_icon(self, name, bmp_file, folder=None):
        try:
            print(f"Loading image from: {bmp_file}")
            image = Image.open(bmp_file)
            rotated_image = image.rotate(-90, expand=True)
            rotated_image = rotated_image.convert("RGBA")
            data = rotated_image.getdata()
            new_data = []
            for item in data:
                if item[:3] == (255, 255, 255):
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            rotated_image.putdata(new_data)
            photo = ImageTk.PhotoImage(rotated_image)
            icon_label = tk.Label(self.icon_frame, image=photo, text=name, compound="top", relief="flat", padx=5, pady=5, bg=self.icon_frame.cget("background"))
            icon_label.image = photo
            icon_label.bind("<Enter>", self.on_hover)
            icon_label.bind("<Leave>", self.on_hover_leave)
            if folder:
                icon_label.bind("<Button-1>", lambda e, folder=folder: self.show_game_screen(folder))
            else:
                icon_label.bind("<Button-1>", lambda e, name=name: self.run_game(name))
            self.place_icon(icon_label)
        except FileNotFoundError as e:
            print(f"Error loading image {bmp_file}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def place_icon(self, icon_label):
        current_column = len(self.icon_frame.winfo_children()) % 5
        current_row = len(self.icon_frame.winfo_children()) // 5
        icon_label.grid(row=current_row, column=current_column, padx=self.spacing, pady=self.spacing, sticky="nw")

    def show_game_screen(self, folder):
        # Clear current icons and add back button
        for widget in self.icon_frame.winfo_children():
            widget.destroy()

        back_button = tk.Button(self.icon_frame, text="Back", command=self.show_main_menu)
        back_button.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Store the directory for later use
        self.current_games_directory = os.path.join("Games", folder, "Games")
        
        # Load game icons from the selected folder
        print(f"Checking directory: {self.current_games_directory}")

        if os.path.exists(self.current_games_directory) and os.path.isdir(self.current_games_directory):
            game_folders = ["Game1", "Game2", "Game3"]

            for game_folder in game_folders:
                bmp_file = os.path.join(self.current_games_directory, game_folder, f"{game_folder}.bmp")
                if os.path.exists(bmp_file):
                    game_name = f"Game {game_folder[-1]}"
                    self.create_icon(game_name, bmp_file)
                else:
                    print(f"Error: No {game_folder}.bmp found in '{self.current_games_directory}'")
        else:
            print(f"The directory '{self.current_games_directory}' does not exist or is incorrect.")

    def show_main_menu(self):
        # Clear current icons and restore main menu
        for widget in self.icon_frame.winfo_children():
            widget.destroy()

        self.search_games_directory()

    def on_hover(self, event):
        event.widget.config(bg="#d0e0ff")

    def on_hover_leave(self, event):
        event.widget.config(bg=self.icon_frame.cget("background"))

    def run_game(self, game_name):
        # Determine the directory based on the stored path
        folder_name = f"Game{game_name[-1]}"
        game_directory = os.path.join(self.current_games_directory, folder_name)

        # Build path to SWF file
        swf_file = os.path.join(game_directory, f"{folder_name}.swf")
        if os.path.exists(swf_file):
            ruffle_path = os.path.join(os.path.dirname(__file__), "ruffle.exe")
            if os.path.exists(ruffle_path):
                print(f"Running command: {ruffle_path} {swf_file}")
                subprocess.Popen([ruffle_path, swf_file])
            else:
                print("Error: ruffle.exe not found in the same directory as main.py")
        else:
            print(f"Error: SWF file {swf_file} not found")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
