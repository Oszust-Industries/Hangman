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
        self.completed_words = load_json(self.completed_words_path, {"completedWords": []}).get("completedWords", [])

        # Load all possible achievements
        self.achievements_file_path = os.path.join("Data", "achievements.json")
        self.all_achievements = load_json(self.achievements_file_path, {"achievements": []}).get("achievements", [])


        # Game state variables
        self.secret_word = ""
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
        self.restart_button.clicked.connect(self.restart_game)
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

    def get_default_settings(self):
        """Returns default settings if the file doesn't exist."""
        return {
            "enable_on_screen_keyboard": True,
            "hints_mode": "Auto", # Auto, Always, Never
            "full_word_guessing": "Off", # Auto, On, Off (Changed from Auto to Off as per request)
            "strikes_limit": 6,
            "enable_sound_effects": False,
            "font_size": "Medium", # Small, Medium, Large
            "high_contrast_mode": False,
            "categories": {"Movies": True} # Default category for starting, ensure it's a dict for checkboxes
        }

    def get_button_style(self):
        """Returns the stylesheet for buttons based on high contrast setting."""
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
        """Applies the current settings to the UI elements."""
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
        """Creates the on-screen keyboard buttons in QWERTY layout."""
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
        
        button_size = 60 # Consistent button size

        for row_idx, row_letters in enumerate(keyboard_rows):
            # For the bottom row (ZXCVBNM), create a horizontal layout to center it
            if row_idx == len(keyboard_rows) - 1: # Last row
                bottom_row_h_layout = QHBoxLayout()
                bottom_row_h_layout.addStretch(1) # Push buttons to center
                for letter in row_letters:
                    button = QPushButton(letter)
                    button.setFixedSize(button_size, button_size)
                    button.clicked.connect(lambda _, l=letter: self.process_keyboard_guess(l))
                    button.setStyleSheet(self.get_button_style())
                    bottom_row_h_layout.addWidget(button)
                bottom_row_h_layout.addStretch(1) # Push buttons to center
                
                # Add the QHBoxLayout to the main QGridLayout
                # We need a dummy widget to hold the QHBoxLayout within the QGridLayout
                dummy_widget = QWidget()
                dummy_widget.setLayout(bottom_row_h_layout)
                self.keyboard_layout.addWidget(dummy_widget, row_idx, 0, 1, self.keyboard_layout.columnCount()) # Span all columns
                self.keyboard_layout.setRowStretch(row_idx, 1) # Allow row to expand
            else:
                for col_idx, letter in enumerate(row_letters):
                    button = QPushButton(letter)
                    button.setFixedSize(button_size, button_size)
                    button.clicked.connect(lambda _, l=letter: self.process_keyboard_guess(l))
                    button.setStyleSheet(self.get_button_style())
                    self.keyboard_layout.addWidget(button, row_idx, col_idx)
            
        # Set column stretch to make columns expand evenly for the top rows
        for i in range(self.keyboard_layout.columnCount()):
            self.keyboard_layout.setColumnStretch(i, 1)


    def process_keyboard_guess(self, letter):
        """Handles a guess made via the on-screen keyboard."""
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
        """Returns the word with guessed letters revealed, underscores for unguessed."""
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.secret_word)

    def make_guess(self):
        """Processes a user's guess (letter or word)."""
        guess = self.guess_input.text().strip().upper()
        self.guess_input.clear()

        if not guess:
            return # Do nothing if input is empty

        full_word_guessing_mode = self.settings.get("full_word_guessing", "Off") # Default to Off

        if len(guess) > 1: # Full word guess
            if full_word_guessing_mode == "Off":
                self.incorrect_guesses_in_round += 1
                return
            elif not guess.isalpha():
                return
            if guess == self.secret_word:
                for letter in self.secret_word: # Reveal all letters
                    self.guessed_letters.add(letter)
                self.word_label.setText(self.display_word())
                self.end_game(win=True)
            else:
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
                QMessageBox.warning(self, "Invalid Input", "Please enter a single letter.")
                return

            if guess == " ":
                pass

            if guess in self.guessed_letters:
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
        """Updates the status label based on hints mode or remaining attempts."""
        hints_mode = self.settings.get("hints_mode", "Auto")
        
        if hints_mode == "Always":
            self.status_label.setText(self.word_data_dict.get(self.secret_word.capitalize(), "Guess the hidden word!"))
        elif hints_mode == "Auto":
            half_strikes_limit = self.initial_strikes_limit // 2
            if self.remaining_attempts <= half_strikes_limit:
                self.status_label.setText(self.word_data_dict.get(self.secret_word.capitalize(), "Guess the hidden word!"))
            else:
                self.status_label.setText(f"Remaining Attempts: {self.remaining_attempts}")
        else: # hints_mode == "Never"
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
        """Ends the game immediately, revealing the word."""
        reply = QMessageBox.question(self, "Give Up?",
                                     "Are you sure you want to give up? The word will be revealed.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.word_label.setText(self.secret_word)
            self.end_game(win=False)
        else:
            pass # Continue game if "No" is pressed


    def open_menu(self):
        """Switches to the Main Menu window."""
        self.switch_window("MainMenuWindow")

    def end_game(self, win):
        """Ends the current game, displays result, and prepares for restart."""
        game_duration_seconds = self.stop_game_timer()

        if win:
            QMessageBox.information(self, "You Win!", f"Congratulations! The word was '{self.secret_word}'.")
            
            # Update win count and save completed word
            self.unlocked_data["win_count"] = self.unlocked_data.get("win_count", 0) + 1
            if self.secret_word not in self.unlocked_data.get("unique_words_guessed", []):
                self.unlocked_data["unique_words_guessed"].append(self.secret_word)

            # Add completed word to the separate list
            if self.secret_word not in self.completed_words:
                self.completed_words.append(self.secret_word)
                save_json(self.completed_words_path, {"completedWords": self.completed_words})
            
            # Check for achievements
            self.check_and_unlock_achievement("first_win") # Based on win_count
            
            if self.incorrect_guesses_in_round == 0:
                self.check_and_unlock_achievement("perfect_game")
            
            # Check for Word Collector achievements
            for achievement in self.all_achievements:
                if achievement.get("type") == "unique_words":
                    if len(self.unlocked_data.get("unique_words_guessed", [])) >= achievement.get("threshold"):
                        self.check_and_unlock_achievement(achievement.get("id"))

            # Check for Speed Demon
            for achievement in self.all_achievements:
                if achievement.get("type") == "time_based" and achievement.get("id") == "speed_demon":
                    if game_duration_seconds is not None and game_duration_seconds <= achievement.get("threshold"):
                        self.check_and_unlock_achievement(achievement.get("id"))

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
        """Resets the game state and starts a new round."""
        self.apply_settings() # Re-apply settings in case strikes limit changed
        self.incorrect_guesses_in_round = 0 # Reset for "Perfect Game" achievement
        self.start_game_timer() # Start timer for the new game

        # Load words and their descriptions, now picking a random category each time
        self.word_data_dict, self.current_dlc_theme, self.current_dlc_description = self.load_words()
        
        # Filter out already completed words
        available_words = [word for word in self.word_data_dict.keys() if word not in self.completed_words]

        if available_words:
            self.secret_word = random.choice(available_words).upper()
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
        """Records the start time of the game."""
        self.last_game_start_time = datetime.now()

    def stop_game_timer(self):
        """Stops the game timer and returns the duration in seconds."""
        if self.last_game_start_time:
            duration = (datetime.now() - self.last_game_start_time).total_seconds()
            self.last_game_start_time = None # Reset
            return duration
        return None

    def update_achievement_progress(self, achievement_id, value):
        """Updates the progress for a specific achievement."""
        current_progress = self.unlocked_data["unlockedAchievementsProgress"].get(achievement_id, 0)
        self.unlocked_data["unlockedAchievementsProgress"][achievement_id] = current_progress + value
        save_json(self.unlocked_achievements_path, self.unlocked_data)

    def check_and_unlock_achievement(self, achievement_id):
        """Checks if the conditions for an achievement are met and unlocks it."""
        for achievement in self.all_achievements:
            if achievement.get("id") == achievement_id and achievement_id not in self.unlocked_data.get("unlockedAchievements", []):
                unlocked = False
                if achievement.get("type") == "game_count" and self.unlocked_data.get("win_count", 0) >= achievement.get("threshold"):
                    unlocked = True
                elif achievement.get("type") == "perfect_game" and self.incorrect_guesses_in_round == 0:
                    unlocked = True
                elif achievement.get("type") == "unique_words" and len(self.unlocked_data.get("unique_words_guessed", [])) >= achievement.get("threshold"):
                    unlocked = True
                elif achievement.get("type") == "time_based" and achievement.get("id") == "speed_demon":
                    # This check needs to be done when game ends and time is known
                    # The end_game function already handles calling this with the time_based type
                    pass # Handled by direct call in end_game after getting duration

                if unlocked:
                    self.unlock_achievement(achievement["name"], achievement["description"])
                    break # Only unlock once per game

    def unlock_achievement(self, title, description):
        """Unlocks an achievement, shows a popup, and saves the data."""
        # Find the achievement by title/name to get its ID
        achievement_id = None
        for ach in self.all_achievements:
            if ach["name"] == title:
                achievement_id = ach["id"]
                break

        if achievement_id and achievement_id not in self.unlocked_data.get("unlockedAchievements", []):
            self.unlocked_data["unlockedAchievements"].append(achievement_id) # Store ID, not title
            # Add unlock time
            self.unlocked_data["unlockTimes"][achievement_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            save_json(self.unlocked_achievements_path, self.unlocked_data)
            
            # Show achievement popup
            self.show_achievement_popup(title, description)
        elif not achievement_id:
            print(f"Warning: Attempted to unlock unknown achievement: {title}")

    def show_achievement_popup(self, title, description):
        """Displays a temporary achievement popup in the bottom right corner."""
        popup_text = f"<b>Achievement Unlocked!</b><br>{title}<br><i>{description}</i>"
        self.achievement_popup.setText(popup_text)
        self.achievement_popup.adjustSize() # Adjust size to fit content

        # Position in bottom right
        self.achievement_popup.move(
            self.width() - self.achievement_popup.width() - 20, # 20px right margin
            self.height() - self.achievement_popup.height() - 20 # 20px bottom margin
        )
        self.achievement_popup.show()
        self.achievement_timer.start(5000) # Show for 5 seconds

    def hide_achievement_popup(self):
        """Hides the achievement popup."""
        self.achievement_popup.hide()
        self.achievement_timer.stop()

    def resizeEvent(self, event):
        """Handles window resize events to adjust background image and achievement popup."""
        self.background_image.setGeometry(0, 0, self.width(), self.height())
        # Re-position achievement popup on resize
        if not self.achievement_popup.isHidden():
            self.achievement_popup.move(
                self.width() - self.achievement_popup.width() - 20,
                self.height() - self.achievement_popup.height() - 20
            )
        super().resizeEvent(event)