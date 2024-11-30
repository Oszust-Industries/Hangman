import os
import sys
import json
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog, QCheckBox, QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


# --- Utility Functions ---
def load_json(file_path, default=None):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return default or {}


def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


# --- Achievements Window ---
class AchievementsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Achievements")
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.achievements = load_json("achievements.json", {"unlocked": []})
        self.display_achievements()

    def display_achievements(self):
        achievements_meta = load_json("achievements_meta.json", {})
        unlocked = self.achievements.get("unlocked", [])

        for title, details in achievements_meta.items():
            container = QHBoxLayout()

            # Achievement Image
            if title in unlocked and "image" in details:
                pixmap = QPixmap(details["image"])
                image_label = QLabel()
                image_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
                container.addWidget(image_label)

            # Achievement Title
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold;" if title in unlocked else "color: gray;")
            container.addWidget(title_label)

            # Achievement Description (only if unlocked)
            if title in unlocked and "description" in details:
                description_label = QLabel(details["description"])
                container.addWidget(description_label)

            self.layout.addLayout(container)


# --- Settings Window ---
class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.settings = load_json("settings.json", {"enabled_dlc": []})
        self.dlc_folder = "dlc"
        self.dlc_checkboxes = {}
        self.load_dlc_packs()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(save_button)

    def load_dlc_packs(self):
        if not os.path.exists(self.dlc_folder):
            os.makedirs(self.dlc_folder)

        dlc_files = [f for f in os.listdir(self.dlc_folder) if f.endswith(".json")]

        for dlc in dlc_files:
            dlc_name = os.path.splitext(dlc)[0]
            checkbox = QCheckBox(dlc_name)
            checkbox.setChecked(dlc_name in self.settings["enabled_dlc"])
            self.layout.addWidget(checkbox)
            self.dlc_checkboxes[dlc_name] = checkbox

    def save_settings(self):
        self.settings["enabled_dlc"] = [name for name, box in self.dlc_checkboxes.items() if box.isChecked()]
        save_json("settings.json", self.settings)
        QMessageBox.information(self, "Settings", "Settings saved!")
        self.close()


# --- Game Window ---
class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman Game")
        self.setMinimumSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.settings = load_json("settings.json", {"enabled_dlc": []})
        self.word_pool = self.load_words()
        self.secret_word = random.choice(self.word_pool).upper()
        self.guessed_letters = set()
        self.remaining_attempts = 6

        self.achievements = load_json("achievements.json", {"unlocked": []})

        self.word_label = QLabel(self.display_word())
        self.word_label.setStyleSheet("font-size: 24px;")
        self.layout.addWidget(self.word_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.guess_input = QLineEdit()
        self.guess_input.setMaxLength(1)
        self.guess_input.returnPressed.connect(self.make_guess)
        self.layout.addWidget(self.guess_input)

        self.status_label = QLabel(f"Remaining Attempts: {self.remaining_attempts}")
        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_game)
        self.restart_button.hide()
        self.layout.addWidget(self.restart_button)

    def load_words(self):
        word_pool = []
        dlc_folder = "dlc"
        enabled_dlc = self.settings.get("enabled_dlc", [])
        for dlc_name in enabled_dlc:
            dlc_path = os.path.join(dlc_folder, f"{dlc_name}.json")
            dlc_words = load_json(dlc_path, [])
            word_pool.extend(dlc_words)
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


# --- Main Menu ---
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman - Main Menu")
        self.setMinimumSize(400, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        title_label = QLabel("Hangman Game")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center;")
        self.layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        play_button = QPushButton("Play Game")
        play_button.clicked.connect(self.start_game)
        self.layout.addWidget(play_button)

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        self.layout.addWidget(settings_button)

        achievements_button = QPushButton("Achievements")
        achievements_button.clicked.connect(self.show_achievements)
        self.layout.addWidget(achievements_button)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        self.layout.addWidget(quit_button)

    def start_game(self):
        self.close()
        self.game_window = GameWindow()
        self.game_window.show()

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.exec()

    def show_achievements(self):
        self.achievements_window = AchievementsWindow()
        self.achievements_window.exec()


# --- Main Program ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec())
