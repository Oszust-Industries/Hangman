import os
import sys
import json
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog, QCheckBox, QMessageBox, QScrollArea, QWidget, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt

# --- Utility Functions ---
def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def load_json(file_path, default=None):
    """Load JSON data from a file, returning default if file doesn't exist."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        return default if default is not None else {}


class GameWindow(QWidget):
    def __init__(self, switch_window_callback):
        super().__init__()
        self.setWindowTitle("Hangman Game")

        # Callback for switching to other windows (like Main Menu)
        self.switch_window = switch_window_callback

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)  # Directly set the layout

        # Header with Menu Button
        self.header_layout = QHBoxLayout()
        
        self.menu_button = QPushButton("Menu")
        self.menu_button.clicked.connect(self.open_menu)
        self.header_layout.addWidget(self.menu_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Add header layout to the main layout
        self.layout.addLayout(self.header_layout)

        # Game UI components
        self.word_label = QLabel("Hangman")
        self.word_label.setStyleSheet("font-size: 24px;")
        self.layout.addWidget(self.word_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.guess_input = QLineEdit()
        self.layout.addWidget(self.guess_input)

        self.status_label = QLabel("Remaining Attempts: 6")
        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_game)
        self.restart_button.hide()  # Hide initially
        self.layout.addWidget(self.restart_button)

    def open_menu(self):
        """Open the Main Menu or Settings"""
        # Call the passed callback function to switch the window
        self.switch_window("settings")

    def load_words(self):
        word_pool = []
        dlc_folder = "dlc"
        enabled_dlc = self.settings.get("enabled_dlc", [])
        for dlc_name in enabled_dlc:
            dlc_path = os.path.join(dlc_folder, f"{dlc_name}.json")
            dlc_words = load_json(dlc_path, [])
            for category, words in dlc_words.items():
                for word in words:
                    word_pool.append(word)
        if not word_pool:
            word_pool = ["DEFAULT"]
        return word_pool

    def display_word(self):
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.secret_word)

    def make_guess(self):
        guess = self.guess_input.text().upper()
        self.guess_input.clear()

        if not guess.isalpha() or len(guess) != 1:
            QMessageBox.warning(self, "Invalid Input", "Please enter a single letter.")
            return

        if guess in self.guessed_letters:
            QMessageBox.warning(self, "Already Guessed", f"You've already guessed '{guess}'.")
            return

        self.guessed_letters.add(guess)

        if guess in self.secret_word:
            self.word_label.setText(self.display_word())
            if "_" not in self.display_word():
                self.unlock_achievement("First Win")
                self.end_game(win=True)
        else:
            self.remaining_attempts -= 1
            self.status_label.setText(f"Remaining Attempts: {self.remaining_attempts}")
            if self.remaining_attempts == 0:
                self.end_game(win=False)

    def open_menu(self):
        """When the Menu button is clicked, switch back to the Main Menu"""
        self.switch_window("MainMenuWindow")  # Call the callback to switch to the main menu

    def end_game(self, win):
        if win:
            QMessageBox.information(self, "You Win!", f"Congratulations! The word was '{self.secret_word}'.")
        else:
            QMessageBox.critical(self, "Game Over", f"You lost! The word was '{self.secret_word}'.")

        self.restart_button.show()
        self.guess_input.setDisabled(True)

    def restart_game(self):
        self.secret_word = random.choice(self.word_pool).upper()
        self.guessed_letters = set()
        self.remaining_attempts = 6
        self.word_label.setText(self.display_word())
        self.status_label.setText(f"Remaining Attempts: {self.remaining_attempts}")
        self.guess_input.setDisabled(False)
        self.restart_button.hide()

    def unlock_achievement(self, title):
        if title not in self.achievements["unlocked"]:
            self.achievements["unlocked"].append(title)
            save_json("achievements.json", self.achievements)
            QMessageBox.information(self, "Achievement Unlocked!", f"You unlocked: {title}!")
