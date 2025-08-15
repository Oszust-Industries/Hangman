import json, os, sys
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QSpinBox, QComboBox, QPushButton, QScrollArea, QWidget, QGroupBox, QFormLayout, QHBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

basePath = os.path.join(os.getenv('APPDATA'), 'Oszust Industries')
hangmanPath = os.path.join(basePath, 'Hangman Game')
settings_file = os.path.join(hangmanPath, 'settings.json')
unlocked_achievements_file = os.path.join(hangmanPath, 'unlockedAchievements.json')
completed_words_file = os.path.join(hangmanPath, 'completedWords.json')
DLC_DIR = resource_path("DLC")

class SettingsWindow(QDialog):
    def __init__(self, switchWindowCallback):
        super().__init__()

        self.switchWindow = switchWindowCallback

        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 550)

        # Initialize categories dictionary 
        self.categories = {}
        self.load_categories_from_dlc()

        # Main layout
        layout = QVBoxLayout(self)

        # Scrollable area setup
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget()
        scrollLayout = QVBoxLayout(scrollContent)
        scrollLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        ### Gameplay Settings
        gameplayBox = QGroupBox("Gameplay Settings")
        gameplayLayout = QFormLayout()

        # On-Screen Keyboard
        self.keyboardCheckbox = QCheckBox("Enable On-Screen Keyboard")
        self.keyboardCheckbox.setChecked(True)
        gameplayLayout.addRow(self.keyboardCheckbox)

        # Hints Mode (Auto, Always, Never)
        self.hintsCombo = QComboBox()
        self.hintsCombo.addItems(["Auto", "Always", "Never"])
        gameplayLayout.addRow("Hints Mode:", self.hintsCombo)

        # Full Word Guessing (On, Off)
        self.guessCombo = QComboBox()
        self.guessCombo.addItems(["On", "Off"])
        self.guessCombo.setCurrentIndex(1)
        gameplayLayout.addRow("Full Word Guessing:", self.guessCombo)

        # Strikes Limit
        self.strikesSpinbox = QSpinBox()
        self.strikesSpinbox.setRange(3, 6)
        self.strikesSpinbox.setValue(6)
        gameplayLayout.addRow("Strikes Limit:", self.strikesSpinbox)

        gameplayBox.setLayout(gameplayLayout)
        scrollLayout.addWidget(gameplayBox)

        ### Audio Settings
        #audioBox = QGroupBox("Audio Settings")
        #audioLayout = QFormLayout()
        #self.soundCheckbox = QCheckBox("Enable Sound Effects")
        #audioLayout.addRow(self.soundCheckbox)
        #audioBox.setLayout(audioLayout)
        #scrollLayout.addWidget(audioBox)

        ### Accessibility Settings
        #accessibilityBox = QGroupBox("Accessibility Settings")
        #accessibilityLayout = QFormLayout()
        #self.fontSizeCombo = QComboBox()
        #self.fontSizeCombo.addItems(["Small", "Medium", "Large"])
        #self.fontSizeCombo.setCurrentIndex(1)
        #self.highContrastCheckbox = QCheckBox("Enable High Contrast Mode")
        #accessibilityLayout.addRow("Font Size:", self.fontSizeCombo)
        #accessibilityLayout.addRow(self.highContrastCheckbox)
        #accessibilityBox.setLayout(accessibilityLayout)
        #scrollLayout.addWidget(accessibilityBox)

        ### Categories & DLC Selection
        categoryBox = QGroupBox("Categories & DLC")
        categoryLayout = QVBoxLayout()
        for cb in self.categories.values():
            categoryLayout.addWidget(cb)
        categoryLayout.addStretch(1)

        categoryBox.setLayout(categoryLayout)
        scrollLayout.addWidget(categoryBox)

        ### Data Management
        dataBox = QGroupBox("Data Management")
        dataLayout = QVBoxLayout()
        self.resetAchievementsButton = QPushButton("Reset Achievements")
        self.resetHistoryButton = QPushButton("Reset Game History")
        self.resetSettingsButton = QPushButton("Reset All Settings")

        # Connect reset buttons to their functions
        self.resetAchievementsButton.clicked.connect(self.resetAchievements)
        self.resetHistoryButton.clicked.connect(self.resetHistory)
        self.resetSettingsButton.clicked.connect(self.resetSettings)

        dataLayout.addWidget(self.resetAchievementsButton)
        dataLayout.addWidget(self.resetHistoryButton)
        dataLayout.addWidget(self.resetSettingsButton)
        dataBox.setLayout(dataLayout)
        scrollLayout.addWidget(dataBox)

        # Add scroll content to scroll area
        scrollArea.setWidget(scrollContent)
        layout.addWidget(scrollArea)

        # Save & Close button
        self.saveButton = QPushButton("Save and Close")
        self.saveButton.clicked.connect(self.saveAndClose)
        layout.addWidget(self.saveButton)

        self.load_settings()

    def load_categories_from_dlc(self):
        os.makedirs(DLC_DIR, exist_ok=True)

        for filename in os.listdir(DLC_DIR):
            if filename.endswith(".json"):
                category_name = os.path.splitext(filename)[0]
                checkbox = QCheckBox(category_name)
                checkbox.setChecked(True)
                self.categories[category_name] = checkbox

    def load_settings(self):
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                self.keyboardCheckbox.setChecked(settings.get('enable_on_screen_keyboard', True))
                self.hintsCombo.setCurrentText(settings.get('hints_mode', "Auto"))
                self.guessCombo.setCurrentText(settings.get('full_word_guessing', "Off"))
                self.strikesSpinbox.setValue(settings.get('strikes_limit', 6))
                #self.soundCheckbox.setChecked(settings.get('enable_sound_effects', False))
                #self.fontSizeCombo.setCurrentText(settings.get('font_size', "Medium"))
                #self.highContrastCheckbox.setChecked(settings.get('enable_high_contrast_mode', False))

                # Load category settings for dynamically created checkboxes
                loaded_categories_state = settings.get('categories', {})
                for category_name, checkbox in self.categories.items():
                    checkbox.setChecked(loaded_categories_state.get(category_name, True))

                print("Settings loaded successfully.")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {settings_file}. File might be corrupted.")
            except Exception as e:
                print(f"An error occurred while loading settings: {e}")
        else:
            print("Settings file not found. Using default settings.")
            self.save_settings()


    def save_settings(self):
        settings = {
            'enable_on_screen_keyboard': self.keyboardCheckbox.isChecked(),
            'hints_mode': self.hintsCombo.currentText(),
            'full_word_guessing': self.guessCombo.currentText(),
            'strikes_limit': self.strikesSpinbox.value(),
            'enable_sound_effects': False, #DEFAULT - self.soundCheckbox.isChecked()
            'font_size': "Medium", #DEFAULT - self.fontSizeCombo.currentText()
            'enable_high_contrast_mode': False, #DEFAULT - self.highContrastCheckbox.isChecked()
            'categories': {name: cb.isChecked() for name, cb in self.categories.items()}
        }

        # Ensure the directory exists
        os.makedirs(hangmanPath, exist_ok=True)

        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print("Settings saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving settings: {e}")

    def saveAndClose(self):
        self.save_settings()
        self.switchWindow("MainMenuWindow")
        self.close()

    def resetAchievements(self):
        reply = QMessageBox.question(self, "Reset Achievements",
                                     "Are you sure you want to reset all achievements? This cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Reset the achievement data in the JSON file
            default_unlocked_data = {"unlockedAchievements": [], "unlockedAchievementsProgress": {}, "unlockTimes": {}, "win_count": 0, "unique_words_guessed": []}
            try:
                # Ensure the directory exists before saving
                os.makedirs(os.path.dirname(unlocked_achievements_file), exist_ok=True)
                with open(unlocked_achievements_file, 'w', encoding='utf-8') as f:
                    json.dump(default_unlocked_data, f, indent=4)
                QMessageBox.information(self, "Achievements Reset", "All achievement data has been reset.")
                print("Achievements Reset Successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset achievements: {e}")
                print(f"Error resetting achievements: {e}")

    def resetHistory(self):
        reply = QMessageBox.question(self, "Reset Game History",
                                     "Are you sure you want to reset your game history? This will allow you to play previously completed words again.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear the completed words file
                os.makedirs(os.path.dirname(completed_words_file), exist_ok=True)
                with open(completed_words_file, 'w', encoding='utf-8') as f:
                    json.dump({"completedWords": []}, f, indent=4)
                QMessageBox.information(self, "Game History Reset", "Your game history (completed words) has been reset.")
                print("Game History (Completed Words) Reset Successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset game history: {e}")
                print(f"Error resetting game history: {e}")

    def resetSettings(self):
        # Reset default values for general settings
        self.keyboardCheckbox.setChecked(True)
        self.hintsCombo.setCurrentIndex(0) # Auto
        self.guessCombo.setCurrentIndex(1) # Off
        self.strikesSpinbox.setValue(6)
        #self.soundCheckbox.setChecked(False)
        #self.fontSizeCombo.setCurrentIndex(1) # Medium
        #self.highContrastCheckbox.setChecked(False)

        for cb in self.categories.values():
            cb.setChecked(True)
        print("Settings Reset to Defaults")
        self.save_settings()