import json, sys, random, os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog, QCheckBox, QMessageBox, QScrollArea, QWidget, QFrame, QProgressBar, QGridLayout, QSpacerItem
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor, QImage
from PyQt6.QtCore import Qt, QRect, QTimer
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def save_json(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"Error saving JSON to '{file_path}': {e}")

def load_json(file_path, default=None):
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
        self.switch_window = switch_window_callback
        self.setWindowTitle("Hangman Game")

        # Path to settings file (assuming it's in APPDATA)
        self.app_data_path = os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game')
        self.settings_file_path = os.path.join(self.app_data_path, 'settings.json')
        self.unlocked_achievements_path = os.path.join(self.app_data_path, 'unlockedAchievements.json')
        self.completed_words_path = os.path.join(self.app_data_path, 'completedWords.json')

        # Load settings, achievements, and completed words
        self.settings = load_json(self.settings_file_path, self.get_default_settings())
        # Ensure default values for tracking are present
        default_unlocked_data = {"unlockedAchievements": [], "unlockedAchievementsProgress": {}, "unlockTimes": {}, "win_count": 0, "unique_words_guessed": []}
        self.unlocked_data = load_json(self.unlocked_achievements_path, default_unlocked_data)
        self.completed_words = load_json(self.completed_words_path, {})

        # Load all possible achievements
        self.achievements_file_path = resource_path(os.path.join("Data", "achievements.json"))
        self.all_achievements = load_json(self.achievements_file_path, default={})

        # Game state variables
        self.secret_word = ""
        self.secret_word_key = ""
        self.guessed_letters = set()
        self.remaining_attempts = 0
        self.current_dlc_theme = "Base Game" # Stores the name of the current DLC/Category
        self.current_dlc_description = "Guess the hidden word!" # Stores the description
        self.word_data_dict = {} # Stores {word: description} for the current category
        self.initial_strikes_limit = self.settings.get("strikes_limit", 6) # Store initial strikes limit for half-guesses calculation
        self.incorrect_guesses_in_round = 0 # Track incorrect guesses for "Perfect Game" achievement
        self.last_game_start_time = None # To track game duration for "Speed Demon" achievement

        # Set background image
        self.background_image = QLabel(self)
        self.background_image.setPixmap(QPixmap(resource_path(os.path.join("Data", "woodBackground.jpg"))))
        self.background_image.setScaledContents(True)
        self.background_image.setGeometry(0, 0, self.width(), self.height())

        # Main layout (vertical)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20) # Add some padding
        self.setLayout(self.main_layout)

        # Header with Menu and Give Up Buttons
        self.header_layout = QHBoxLayout()
        self.menu_button = QPushButton("Menu")
        self.menu_button.clicked.connect(self.open_menu)
        self.menu_button.setStyleSheet(self.get_button_style())
        self.header_layout.addWidget(self.menu_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # DLC Theme Label (new)
        self.dlc_theme_label = QLabel(self.current_dlc_theme)
        self.dlc_theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dlc_theme_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.header_layout.addWidget(self.dlc_theme_label, alignment=Qt.AlignmentFlag.AlignCenter)


        self.give_up_button = QPushButton("Give Up") # Renamed from hint_button
        self.give_up_button.clicked.connect(self.give_up) # Connected to new give_up method
        self.give_up_button.setStyleSheet(self.get_button_style())
        self.header_layout.addWidget(self.give_up_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(self.header_layout)

        # Hangman image that changes based on remaining attempts
        self.hangman_image = QLabel(self)
        self.hangman_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.hangman_image)

        # Word display label
        self.word_label = QLabel("")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.word_label)

        # Status label for attempts / DLC description
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Input and Guess Button Layout
        self.input_layout = QHBoxLayout()
        self.guess_input = QLineEdit()
        self.guess_input.setPlaceholderText("Enter a letter or word")
        self.guess_input.returnPressed.connect(self.make_guess) # Allow pressing Enter
        self.input_layout.addWidget(self.guess_input)

        self.guess_button = QPushButton("Guess")
        self.guess_button.clicked.connect(self.make_guess)
        self.guess_button.setStyleSheet(self.get_button_style())
        self.input_layout.addWidget(self.guess_button)
        self.main_layout.addLayout(self.input_layout)

        # On-Screen Keyboard
        self.keyboard_frame = QFrame(self)
        self.keyboard_layout = QGridLayout(self.keyboard_frame)
        self.keyboard_frame.setLayout(self.keyboard_layout)
        self.create_on_screen_keyboard()
        self.main_layout.addWidget(self.keyboard_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Restart Button
        self.restart_button = QPushButton("Play Again")
        self.restart_button.clicked.connect(self.restartButton)
        self.restart_button.setStyleSheet(self.get_button_style())
        self.restart_button.hide() # Hide initially
        self.main_layout.addWidget(self.restart_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.apply_settings() # Apply initial settings
        self.restart_game() # Start a new game

        # Achievement popup (initially hidden)
        self.achievement_popup = QLabel(self)
        self.achievement_popup.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
        """)
        self.achievement_popup.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.achievement_popup.hide()
        self.achievement_timer = QTimer(self)
        self.achievement_timer.timeout.connect(self.hide_achievement_popup)

        self.check_and_unlock_achievement("Achievement_Welcome")

    def restartButton(self):
        self.check_and_unlock_achievement("Achievement_Keep_Playing")
        self.restart_game()

    def get_default_settings(self):
        return {
            "enable_on_screen_keyboard": True,
            "hints_mode": "Auto",
            "full_word_guessing": "Off",
            "strikes_limit": 6,
            "enable_sound_effects": False,
            "font_size": "Medium",
            "high_contrast_mode": False,
            "categories": {"Movies": True}
        }

    def refresh_data_from_files(self):
        # Define a default structure for achievements in case the file is not found
        default_unlocked_data = {
            "unlockedAchievements": [],
            "unlockedAchievementsProgress": {},
            "unlockTimes": {},
            "win_count": 0,
            "unique_words_guessed": []
        }
        # Reload the achievements data from the specified path
        self.unlocked_data = load_json(self.unlocked_achievements_path, default_unlocked_data)

        # Reload the completed words data from the specified path
        # It's set to a dictionary by default, to handle the new category structure
        self.completed_words = load_json(self.completed_words_path, {})

    def get_button_style(self):
        if self.settings.get("high_contrast_mode", False):
            return """
                QPushButton {
                    background-color: #FFFF00; /* Yellow */
                    color: #000000; /* Black */
                    font-size: 18px;
                    padding: 8px 15px;
                    border-radius: 8px;
                    border: 2px solid #000000;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FFD700; /* Gold */
                    border: 2px solid #000000;
                }
                QPushButton:disabled {
                    background-color: #808080; /* Gray */
                    color: #C0C0C0;
                    border: 2px solid #505050;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #444;
                    color: white;
                    font-size: 18px;
                    padding: 8px 15px;
                    border-radius: 8px;
                    border: 2px solid white;
                }
                QPushButton:hover {
                    background-color: #666;
                    border: 2px solid #2997ff;
                }
                QPushButton:disabled {
                    background-color: #808080;
                    color: #C0C0C0;
                    border: 2px solid #505050;
                }
            """

    def apply_settings(self):
        # Load latest settings in case they were changed in SettingsWindow
        self.settings = load_json(self.settings_file_path, self.get_default_settings())

        # High Contrast Mode
        if self.settings.get("high_contrast_mode", False):
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(0, 0, 0)) # Black background
            palette.setColor(QPalette.WindowText, QColor(255, 255, 0)) # Yellow text
            palette.setColor(QPalette.Base, QColor(50, 50, 50)) # Dark gray for input fields
            palette.setColor(QPalette.Text, QColor(255, 255, 0)) # Yellow text for input fields
            self.setPalette(palette)
            self.setStyleSheet("QLabel { color: yellow; } QLineEdit { background-color: #323232; color: yellow; border: 1px solid yellow; }")
            self.background_image.hide() # Hide background image in high contrast
        else:
            self.setPalette(QApplication.instance().palette()) # Reset to default palette
            self.setStyleSheet("") # Clear custom stylesheet
            self.background_image.show() # Show background image

        # Font Size
        font_size_setting = self.settings.get("font_size", "Medium")
        if font_size_setting == "Small":
            font_size = 18
        elif font_size_setting == "Large":
            font_size = 30
        else: # Medium
            font_size = 24

        self.word_label.setFont(QFont("Arial", font_size))
        self.status_label.setFont(QFont("Arial", int(font_size * 0.75))) # Slightly smaller for status
        self.guess_input.setFont(QFont("Arial", int(font_size * 0.8)))
        self.dlc_theme_label.setFont(QFont("Arial", int(font_size * 0.85))) # Adjust DLC theme font size

        # Update button styles for high contrast
        self.menu_button.setStyleSheet(self.get_button_style())
        self.give_up_button.setStyleSheet(self.get_button_style()) # Updated button name
        self.guess_button.setStyleSheet(self.get_button_style())
        self.restart_button.setStyleSheet(self.get_button_style())
        for button in self.keyboard_frame.findChildren(QPushButton):
            button.setStyleSheet(self.get_button_style())

        # On-Screen Keyboard Visibility
        self.keyboard_frame.setVisible(self.settings.get("enable_on_screen_keyboard", True)) # Default to True

        # Give Up Button Visibility (always visible, but its function changes)
        self.give_up_button.setVisible(True)

        # Strikes Limit
        self.remaining_attempts = self.settings.get("strikes_limit", 6)
        self.initial_strikes_limit = self.settings.get("strikes_limit", 6) # Store initial strikes limit for half-guesses calculation
        self.update_status_label() # Update status label based on settings and DLC info
        self.update_hangman_image() # Update hangman image based on new strike limit


    def create_on_screen_keyboard(self):
        # Clear existing buttons if any
        for i in reversed(range(self.keyboard_layout.count())):
            widget = self.keyboard_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        keyboard_rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
    
        button_size = 60  # Consistent button size

        # Reduce vertical spacing for the whole grid
        self.keyboard_layout.setVerticalSpacing(2)  

        for row_idx, row_letters in enumerate(keyboard_rows):
            bottom_row_h_layout = QHBoxLayout()
            bottom_row_h_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
            bottom_row_h_layout.setSpacing(5)  # Space between keys in the same row
            bottom_row_h_layout.addStretch(1)  # Push buttons to center

            for letter in row_letters:
                button = QPushButton(letter)
                button.setFixedSize(button_size, button_size)
                button.clicked.connect(lambda _, l=letter: self.process_keyboard_guess(l))
                button.setStyleSheet(self.get_button_style())
                bottom_row_h_layout.addWidget(button)

            bottom_row_h_layout.addStretch(1)

            dummy_widget = QWidget()
            dummy_widget.setLayout(bottom_row_h_layout)
            self.keyboard_layout.addWidget(dummy_widget, row_idx, 0, 1, self.keyboard_layout.columnCount())
            self.keyboard_layout.setRowStretch(row_idx, 0)  # No vertical expansion

        # Ensure columns still stretch evenly
        for i in range(self.keyboard_layout.columnCount()):
            self.keyboard_layout.setColumnStretch(i, 1)


    def process_keyboard_guess(self, letter):
        self.guess_input.setText(letter)
        self.make_guess()

    def load_words(self):
        """Loads words from JSON files based on enabled categories/DLC.
           Returns (word_data_dict, selected_category_name, category_description).
           word_data_dict will be a dictionary of {word: description}.
        """
        word_data_dict = {}
        dlc_folder = "DLC"
        
        # Get enabled categories from settings
        enabled_categories_dict = self.settings.get("categories", {"Movies": True}) # Default to Movies enabled
        enabled_category_names = [name for name, checked in enabled_categories_dict.items() if checked]

        selected_category_name = "Base Game"
        category_description = "Guess the hidden word!"

        if not enabled_category_names:
            QMessageBox.warning(self, "No Categories Enabled", "Please enable at least one category in settings to play. Using default words.")
            return {"HANGMAN": "A classic word guessing game."}, "Default Words", "A general set of words."

        # Randomly pick one enabled category to load words from for this game
        chosen_category = random.choice(enabled_category_names)
        file_name = f"{chosen_category}.json"
        file_path = resource_path(os.path.join(dlc_folder, file_name))

        if os.path.exists(file_path):
            category_json_data = load_json(file_path, {})
            if isinstance(category_json_data, dict):
                if chosen_category in category_json_data and isinstance(category_json_data[chosen_category], dict):
                    word_data_dict = category_json_data[chosen_category]
                    selected_category_name = chosen_category
                    category_description = f"Words related to {chosen_category}."
                else:
                    print(f"Warning: Unexpected JSON structure for category '{chosen_category}' in {file_path}. Expected a dictionary under the category key.")
                    word_data_dict = {"HANGMAN": "A classic word guessing game."}
                    selected_category_name = "Default Words"
                    category_description = "A general set of words."
            else:
                print(f"Warning: Unexpected top-level JSON structure in {file_path}. Expected a dictionary.")
                word_data_dict = {"HANGMAN": "A classic word guessing game."}
                selected_category_name = "Default Words"
                category_description = "A general set of words."
        else:
            print(f"Warning: Category file not found: {file_path}. Using default words.")
        
        if not word_data_dict:
            word_data_dict = {"HANGMAN": "A classic word guessing game."}
            selected_category_name = "Default Words"
            category_description = "A general set of words."
            QMessageBox.warning(self, "No Words Loaded", "No words found for selected categories or files are missing/invalid. Using default words.")
        
        return word_data_dict, selected_category_name, category_description

    def display_word(self):
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.secret_word)

    def make_guess(self):
        guess = self.guess_input.text().strip().upper()
        self.guess_input.clear()

        if not guess:
            return # Do nothing if input is empty

        self.check_and_unlock_achievement("Achievement_Welcome")

        full_word_guessing_mode = self.settings.get("full_word_guessing", "Off") # Default to Off

        if len(guess) > 1: # Full word guess
            if full_word_guessing_mode == "Off":
                self.incorrect_guesses_in_round += 1
                return
            elif not guess.isalpha():
                return
            if guess == self.secret_word:
                self.check_and_unlock_achievement("Achievement_Solve_Correct")
                if len(self.guessed_letters) == 0:
                    self.check_and_unlock_achievement("Achievement_Solve_Correct_No_Help")
                for letter in self.secret_word: # Reveal all letters
                    self.guessed_letters.add(letter)
                self.word_label.setText(self.display_word())
                self.end_game(win=True)
            else:
                self.check_and_unlock_achievement("Achievement_Solve_Wrong")
                self.remaining_attempts -= 1
                self.incorrect_guesses_in_round += 1
                self.update_status_label()
                self.update_hangman_image()
                if self.remaining_attempts == 0:
                    self.end_game(win=False)
                else:
                    QMessageBox.information(self, "Incorrect Word!", f"'{guess}' is not the word. You lost 1 attempt.")

        else: # Single letter guess
            if not guess.isalpha() and guess != " ": # Check for actual letters or space
                self.check_and_unlock_achievement("Achievement_Alphabet")
                QMessageBox.warning(self, "Invalid Input", "Please enter a single letter.")
                return

            if guess == " ":
                pass

            if guess in self.guessed_letters:
                self.check_and_unlock_achievement("Achievement_Same_Letter")
                QMessageBox.warning(self, "Already Guessed", f"You've already guessed '{guess}'.")
                return

            self.guessed_letters.add(guess)
            # Disable keyboard button for guessed letter
            for button in self.keyboard_frame.findChildren(QPushButton):
                if button.text() == guess:
                    button.setDisabled(True)
                    break

            if guess in self.secret_word:
                self.word_label.setText(self.display_word())
                if "_" not in self.display_word():
                    self.end_game(win=True)
            else:
                self.remaining_attempts -= 1
                self.incorrect_guesses_in_round += 1 # Track incorrect guesses
                self.update_status_label()
                self.update_hangman_image()
                if self.remaining_attempts == 0:
                    self.end_game(win=False)

    def update_status_label(self):
        hints_mode = self.settings.get("hints_mode", "Auto")

        if hints_mode == "Always":
            self.status_label.setText(self.word_data_dict.get(self.secret_word_key, "Guess the hidden word!"))
        elif hints_mode == "Auto":
            half_strikes_limit = self.initial_strikes_limit // 2
            if self.remaining_attempts <= half_strikes_limit:
                self.status_label.setText(self.word_data_dict.get(self.secret_word_key, "Guess the hidden word!"))
            else:
                self.status_label.setText(f"Remaining Attempts: {self.remaining_attempts}")
        else:
            self.status_label.setText(f"Remaining Attempts: {self.remaining_attempts}")

    def update_hangman_image(self):
        max_attempts = self.settings.get("strikes_limit", 6)
        total_images = 6

        # Calculate fraction of strikes taken
        strikes_taken = max_attempts - self.remaining_attempts
        progress = strikes_taken / max_attempts  # value between 0 and 1

        # Map to closest image index
        display_image_index = round(progress * total_images)

        # Ensure within bounds
        display_image_index = max(0, min(total_images, display_image_index))

        image_path = resource_path(os.path.join("Data", f"hangman_{display_image_index}.jpg"))

        pixmap = QPixmap(image_path)

        if os.path.exists(image_path):
            pixmap.load(image_path)
        else:
            # Create a simple blank image if the specific hangman image is not found
            blank_image = QImage(200, 200, QImage.Format.Format_ARGB32)
            blank_image.fill(QColor(0, 0, 0, 0)) # Fully transparent
            pixmap = QPixmap.fromImage(blank_image)
            print(f"Warning: Hangman image not found: {image_path}. Using a blank placeholder.")

        self.hangman_image.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def give_up(self):
        reply = QMessageBox.question(self, "Give Up?",
                                     "Are you sure you want to give up? The word will be revealed.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.word_label.setText(self.secret_word)
            self.end_game(win=False)
        else:
            pass # Continue game if "No" is pressed


    def open_menu(self):
        self.check_and_unlock_achievement("Achievement_Stop_Playing")
        if len(self.guessed_letters) > 0:
            self.check_and_unlock_achievement("Achievement_Terminate")
        self.switch_window("MainMenuWindow")

    def end_game(self, win):

        total_completed_words = self.unlocked_data["unlockedAchievementsProgress"].get("Achievement_All_Topics", 0)
        self.unlocked_data["unlockedAchievementsProgress"]["Achievement_All_Topics"] = (total_completed_words + 1)

        if win:
            QMessageBox.information(self, "You Win!", f"Congratulations! The word was '{self.secret_word}'.")
            
            self.check_and_unlock_achievement("Achievement_Winner")

            if self.remaining_attempts == 1:
                self.check_and_unlock_achievement("Achievement_Close_Call")

            if self.settings.get("hints_mode", "Auto") == "Never":
                self.check_and_unlock_achievement("Achievement_Hard_Mode")

            # Update win count and save completed word

            if "unique_words_guessed" not in self.unlocked_data:
                self.unlocked_data["unique_words_guessed"] = []

            self.unlocked_data["win_count"] = self.unlocked_data.get("win_count", 0) + 1
            if self.secret_word not in self.unlocked_data.get("unique_words_guessed", []):
                self.unlocked_data["unique_words_guessed"].append(self.secret_word)

            # Check if the word is already in the completed list for its category
            completed_in_category = self.completed_words.get(self.current_dlc_theme, [])
            if self.secret_word not in completed_in_category:
                # If not, add it to the category list and save the file
                if self.current_dlc_theme not in self.completed_words:
                    self.completed_words[self.current_dlc_theme] = []
                self.completed_words[self.current_dlc_theme].append(self.secret_word)
                save_json(self.completed_words_path, self.completed_words)

                # Get the new count of completed words for the current category
                new_completed_count = len(self.completed_words.get(self.current_dlc_theme, []))
                
                # Get the current progress for this specific category-based achievement
                # We assume the achievement_id is the same as the category name (e.g., "Animals")
                match self.current_dlc_theme:
                    case "Animals":
                        achievementThemeName = "Achievement_All_Animals"
                    case "Baseball Teams":
                        achievementThemeName = "Achievement_All_Baseball"
                    case "Basketball Teams":
                        achievementThemeName = "Achievement_All_Basketball"
                    case "Big Ten Colleges":
                        achievementThemeName = "Achievement_All_Big_Ten_Colleges"
                    case "Foods":
                        achievementThemeName = "Achievement_All_Foods"
                    case "Football Teams":
                        achievementThemeName = "Achievement_All_Football"
                    case "Hockey Teams":
                        achievementThemeName = "Achievement_All_Hockey"
                    case "Holidays":
                        achievementThemeName = "Achievement_All_Holidays"
                    case "Movies":
                        achievementThemeName = "Achievement_All_Movies"
                    case "Transport":
                        achievementThemeName = "Achievement_All_Transport"
                    case "US Cities":
                        achievementThemeName = "Achievement_All_Cities"

                current_progress = self.unlocked_data["unlockedAchievementsProgress"].get(achievementThemeName, 0)
                print(f"Current progress for {achievementThemeName}: {current_progress}, New completed count: {new_completed_count}")
                
                # Only update the progress if the new count is higher
                if new_completed_count > current_progress:
                    self.unlocked_data["unlockedAchievementsProgress"][achievementThemeName] = new_completed_count
                    
            # Check for win-related achievements and save all progress
            save_json(self.unlocked_achievements_path, self.unlocked_data)
            self.check_and_unlock_achievement()

        else:
            # If not a win, and the game wasn't given up, show the "You Lose" message here.
            # If it was a give up, the message is handled by give_up()
            if self.remaining_attempts == 0 and self.word_label.text() != self.secret_word:
                 QMessageBox.information(self, "You Lose!", f"You ran out of attempts! The word was '{self.secret_word}'.")
        
        save_json(self.unlocked_achievements_path, self.unlocked_data) # Save achievement progress

        self.guess_input.setDisabled(True)
        self.guess_button.setDisabled(True)
        self.give_up_button.setDisabled(True) # Disable give up button
        for button in self.keyboard_frame.findChildren(QPushButton):
            button.setDisabled(True)
        self.restart_button.show()

    def restart_game(self):
        self.refresh_data_from_files()
        self.apply_settings() # Re-apply settings in case strikes limit changed
        self.incorrect_guesses_in_round = 0 # Reset for "Perfect Game" achievement
        self.start_game_timer() # Start timer for the new game

        # Load words and their descriptions, now picking a random category each time
        self.word_data_dict, self.current_dlc_theme, self.current_dlc_description = self.load_words()
        
        # Get the list of completed words for the current category, or an empty list if none exist
        completed_in_current_category = self.completed_words.get(self.current_dlc_theme, [])
        # Filter the word list based on words not yet completed in this category
        available_words = [word for word in self.word_data_dict.keys() if word not in completed_in_current_category]

        if available_words:
            self.secret_word_key = random.choice(available_words)
            self.secret_word = self.secret_word_key.upper()
        else:
            self.secret_word = "HANGMAN" # Fallback if all words in chosen categories are completed
            self.current_dlc_theme = "Default Words"
            self.current_dlc_description = "A general set of words (all words completed in enabled categories)."
            QMessageBox.information(self, "No New Words", "All words in the enabled categories have been completed! Playing with a default word. You can reset game history in settings to play them again.")


        self.guessed_letters = set()
        self.remaining_attempts = self.settings.get("strikes_limit", 6) # Reset remaining attempts

        # Automatically reveal characters in the secret word
        for char in self.secret_word:
            if char == ' ':
                self.guessed_letters.add(' ')
            if char == ',':
                self.guessed_letters.add(',')

        self.word_label.setText(self.display_word())
        self.update_status_label() # Update status label based on current game state
        self.dlc_theme_label.setText(self.current_dlc_theme) # Update DLC theme label

        self.guess_input.setDisabled(False)
        self.guess_button.setDisabled(False)
        self.give_up_button.setDisabled(False) # Re-enable give up button for new game
        self.restart_button.hide()

        # Re-enable all keyboard buttons
        for button in self.keyboard_frame.findChildren(QPushButton):
            button.setDisabled(False)
        
        self.update_hangman_image() # Reset image for new game

    def start_game_timer(self):
        self.last_game_start_time = datetime.now()

    def stop_game_timer(self):
        if self.last_game_start_time:
            duration = (datetime.now() - self.last_game_start_time).total_seconds()
            self.last_game_start_time = None # Reset
            return duration
        return None

    def check_and_unlock_achievement(self, unlockName=None):
        # The category name is the achievement's unique ID
        for achievement_id, achievements_list in self.all_achievements.items():
            # Your structure seems to have a list of achievements per category, even if it's just one.
            # Let's assume for this specific case the list has only one item.
            if achievements_list:
                achievement = achievements_list[0]
            
                # Skip if the achievement is already unlocked
                if achievement_id in self.unlocked_data.get("unlockedAchievements", []):
                    continue

                unlocked = False
                tracker = achievement.get("AchievementProgressTracker")

                if achievement_id == unlockName and unlockName != None:
                    unlocked = True

                # Handle achievements with a progress tracker (threshold-based)
                elif isinstance(tracker, int):
                    current_progress = self.unlocked_data["unlockedAchievementsProgress"].get(achievement_id, 0)
                    if current_progress >= tracker:
                        unlocked = True

                if unlocked:
                    self.unlock_achievement(achievement_id, achievement.get("Name"), achievement.get("Description"))
    
    def unlock_achievement(self, achievement_id, title, description):
        if achievement_id not in self.unlocked_data.get("unlockedAchievements", []):
            self.unlocked_data["unlockedAchievements"].append(achievement_id)
            self.unlocked_data["unlockTimes"][achievement_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            save_json(self.unlocked_achievements_path, self.unlocked_data)
        
            self.show_achievement_popup(achievement_id, title, description)

    def show_achievement_popup(self, achievement_id, title, description):
        icon_path = resource_path(os.path.join("Achievement Icons", achievement_id + ".png"))
        popup_html = f"""
        <div style="display: flex; align-items: flex-start;">
            <img src="{icon_path}" width="48" height="48" style="margin-right: 10px;">
            <div>
                <div style="font-weight: bold; font-size: 14pt;">{title}</div>
                <div style="font-size: 10pt; color: #555;">{description}</div>
            </div>
        </div>
        """
        self.achievement_popup.setText(popup_html)
        self.achievement_popup.adjustSize()

        # Position bottom right
        self.achievement_popup.move(
            self.width() - self.achievement_popup.width() - 20,
            self.height() - self.achievement_popup.height() - 20
        )
        self.achievement_popup.show()
        self.achievement_timer.start(5000)

    def hide_achievement_popup(self):
        self.achievement_popup.hide()
        self.achievement_timer.stop()

    def resizeEvent(self, event):
        self.background_image.setGeometry(0, 0, self.width(), self.height())
        # Re-position achievement popup on resize
        if not self.achievement_popup.isHidden():
            self.achievement_popup.move(
                self.width() - self.achievement_popup.width() - 20,
                self.height() - self.achievement_popup.height() - 20
            )
        super().resizeEvent(event)