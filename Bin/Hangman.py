from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QWidget, QFrame, QGridLayout
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor, QImage
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
import json, sys, random, os

def resource_path(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

def save_json(filePath, data):
    try:
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        with open(filePath, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"Error saving JSON to '{filePath}': {e}")

def load_json(filePath, default=None):
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{filePath}': {e}")
        return default if default is not None else {}

class GameWindow(QWidget):
    def __init__(self, switchWindowCallback):
        super().__init__()
        self.switch_window = switchWindowCallback
        self.setWindowTitle("Hangman Game")

        ## Setting File Paths
        self.appdataPath = os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game')
        self.settingsFilePath = os.path.join(self.appdataPath, 'settings.json')
        self.unlockedAchievementsPath = os.path.join(self.appdataPath, 'unlockedAchievements.json')
        self.completedWordsPath = os.path.join(self.appdataPath, 'completedWords.json')

        ## Load Settings, Achievements, and Completed Words
        self.settings = load_json(self.settingsFilePath, self.get_default_settings())
        defaultUnlockedData = {"unlockedAchievements": [], "unlockedAchievementsProgress": {}, "unlockTimes": {}, "win_count": 0, "unique_words_guessed": []}
        self.unlockedData = load_json(self.unlockedAchievementsPath, defaultUnlockedData)
        self.completedWords = load_json(self.completedWordsPath, {})

        ## Load Achievements
        self.achievementsFilePath = resource_path(os.path.join("Data", "achievements.json"))
        self.allAchievements = load_json(self.achievementsFilePath, default={})

        ## Game State Variables
        self.secretWord = ""
        self.secretWordDisplay = ""
        self.guessedLetters = set()
        self.remainingAttempts = 0
        self.currentDLCTheme = "Base Game"
        self.currentDLCDescription = "Guess the hidden word!"
        self.wordDataDict = {}
        self.initialStrikesLimit = self.settings.get("strikes_limit", 6)

        ## Set Background Image
        self.backgroundImage = QLabel(self)
        self.backgroundImage.setPixmap(QPixmap(resource_path(os.path.join("Data", "woodBackground.jpg"))))
        self.backgroundImage.setScaledContents(True)
        self.backgroundImage.setGeometry(0, 0, self.width(), self.height())

        ## Main Layout (Vertical)
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.mainLayout)

        ## Header with Menu and Give Up Buttons
        self.headerLayout = QHBoxLayout()
        self.menuButton = QPushButton("Menu")
        self.menuButton.clicked.connect(self.open_menu)
        self.menuButton.setStyleSheet(self.get_button_style())
        self.headerLayout.addWidget(self.menuButton, alignment=Qt.AlignmentFlag.AlignLeft)

        ## DLC Theme Label
        self.DLCThemeLabel = QLabel(self.currentDLCTheme)
        self.DLCThemeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLCThemeLabel.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.headerLayout.addWidget(self.DLCThemeLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        ## Give Up Button
        self.giveUpButton = QPushButton("Give Up")
        self.giveUpButton.clicked.connect(self.give_up)
        self.giveUpButton.setStyleSheet(self.get_button_style())
        self.headerLayout.addWidget(self.giveUpButton, alignment=Qt.AlignmentFlag.AlignRight)
        self.mainLayout.addLayout(self.headerLayout)

        ## Dynamic Hangman Image
        self.hangmanImage = QLabel(self)
        self.hangmanImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.hangmanImage)

        ## Word Display Label
        self.wordLabel = QLabel("")
        self.wordLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.wordLabel)

        # Status Label for Attempts and Hints
        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.statusLabel)

        # Input and Guess Button Layout
        self.inputLayout = QHBoxLayout()
        self.guessInput = QLineEdit()
        self.guessInput.setPlaceholderText("Enter a letter or word")
        self.guessInput.returnPressed.connect(self.make_guess)
        self.inputLayout.addWidget(self.guessInput)

        self.guessButton = QPushButton("Guess")
        self.guessButton.clicked.connect(self.make_guess)
        self.guessButton.setStyleSheet(self.get_button_style())
        self.inputLayout.addWidget(self.guessButton)
        self.mainLayout.addLayout(self.inputLayout)

        ## On-Screen Keyboard
        self.keyboardFrame = QFrame(self)
        self.keyboardLayout = QGridLayout(self.keyboardFrame)
        self.keyboardFrame.setLayout(self.keyboardLayout)
        self.create_on_screen_keyboard()
        self.mainLayout.addWidget(self.keyboardFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        ## Restart Button
        self.restartButton = QPushButton("Play Again")
        self.restartButton.clicked.connect(self.restart_button)
        self.restartButton.setStyleSheet(self.get_button_style())
        self.restartButton.hide()
        self.mainLayout.addWidget(self.restartButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.apply_settings()
        self.restart_game()

        ## Achievement Popup
        self.achievementPopup = QLabel(self)
        self.achievementPopup.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
        """)
        self.achievementPopup.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.achievementPopup.hide()
        self.achievementTimer = QTimer(self)
        self.achievementTimer.timeout.connect(self.hide_achievement_popup)

        self.check_and_unlock_achievement("Achievement_Welcome")

    def restart_button(self):
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
        defaultUnlockedData = {
            "unlockedAchievements": [],
            "unlockedAchievementsProgress": {},
            "unlockTimes": {},
            "win_count": 0,
            "unique_words_guessed": []
        }
        # Reload Achievements Data
        self.unlockedData = load_json(self.unlockedAchievementsPath, defaultUnlockedData)

        # Reload Copleted Words Data
        self.completedWords = load_json(self.completedWordsPath, {})

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
        ## Load Settings
        self.settings = load_json(self.settingsFilePath, self.get_default_settings())

        ## High Contrast Mode
        if self.settings.get("high_contrast_mode", False):
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(0, 0, 0))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 0))
            palette.setColor(QPalette.Base, QColor(50, 50, 50))
            palette.setColor(QPalette.Text, QColor(255, 255, 0))
            self.setPalette(palette)
            self.setStyleSheet("QLabel { color: yellow; } QLineEdit { background-color: #323232; color: yellow; border: 1px solid yellow; }")
            self.backgroundImage.hide()
        else:
            self.setPalette(QApplication.instance().palette())
            self.setStyleSheet("")
            self.backgroundImage.show()

        ## Font Size
        fontSizeSetting = self.settings.get("font_size", "Medium")
        if fontSizeSetting == "Small":
            fontSize = 18
        elif fontSizeSetting == "Large":
            fontSize = 30
        else:
            fontSize = 24

        self.wordLabel.setFont(QFont("Arial", fontSize))
        self.statusLabel.setFont(QFont("Arial", int(fontSize * 0.75)))
        self.guessInput.setFont(QFont("Arial", int(fontSize * 0.8)))
        self.DLCThemeLabel.setFont(QFont("Arial", int(fontSize * 0.85)))

        ## High Contrast Mode Button Styles
        self.menuButton.setStyleSheet(self.get_button_style())
        self.giveUpButton.setStyleSheet(self.get_button_style())
        self.guessButton.setStyleSheet(self.get_button_style())
        self.restartButton.setStyleSheet(self.get_button_style())
        for button in self.keyboardFrame.findChildren(QPushButton):
            button.setStyleSheet(self.get_button_style())

        ## On-Screen Keyboard Visibility
        self.keyboardFrame.setVisible(self.settings.get("enable_on_screen_keyboard", True))

        ## Give Up Button Visibility
        self.giveUpButton.setVisible(True)

        ## Strikes Limit
        self.remainingAttempts = self.settings.get("strikes_limit", 6)
        self.initialStrikesLimit = self.settings.get("strikes_limit", 6)
        self.update_status_label()
        self.update_hangman_image()


    def create_on_screen_keyboard(self):
        ## Clear Existing Buttons
        for i in reversed(range(self.keyboardLayout.count())):
            widget = self.keyboardLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        keyboardRows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        buttonSize = 60
        self.keyboardLayout.setVerticalSpacing(2)  

        for rowIdx, rowLetters in enumerate(keyboardRows):
            bottomRowHorizontalLayout = QHBoxLayout()
            bottomRowHorizontalLayout.setContentsMargins(0, 0, 0, 0)
            bottomRowHorizontalLayout.setSpacing(5)
            bottomRowHorizontalLayout.addStretch(1)

            for letter in rowLetters:
                button = QPushButton(letter)
                button.setFixedSize(buttonSize, buttonSize)
                button.clicked.connect(lambda _, l=letter: self.process_keyboard_guess(l))
                button.setStyleSheet(self.get_button_style())
                bottomRowHorizontalLayout.addWidget(button)

            bottomRowHorizontalLayout.addStretch(1)

            dummyWidget = QWidget()
            dummyWidget.setLayout(bottomRowHorizontalLayout)
            self.keyboardLayout.addWidget(dummyWidget, rowIdx, 0, 1, self.keyboardLayout.columnCount())
            self.keyboardLayout.setRowStretch(rowIdx, 0)

        ## Ensure Column Stretching
        for i in range(self.keyboardLayout.columnCount()):
            self.keyboardLayout.setColumnStretch(i, 1)

    def process_keyboard_guess(self, letter):
        self.guessInput.setText(letter)
        self.make_guess()

    def load_words(self):
        ## Get Enabled Categories from Settings
        enabledCategoriesDict = self.settings.get("categories", {"Movies": True})
        enabledCategoryNames = [name for name, checked in enabledCategoriesDict.items() if checked]
        selectedCategoryName = "Base Game"
        categoryDescription = "Guess the hidden word!"
        wordDataDict = {}

        if not enabledCategoryNames:
            QMessageBox.warning(self, "No Categories Enabled", "Please enable at least one category in settings to play. Using default words.")
            return {"HANGMAN": "A classic word guessing game."}, "Default Words", "A general set of words."

        ## Randomly pick one enabled category to load words from for this game
        chosenCategory = random.choice(enabledCategoryNames)
        fileName = f"{chosenCategory}.json"
        filePath = resource_path(os.path.join("DLC", fileName))

        if os.path.exists(filePath):
            categoryJsonData = load_json(filePath, {})
            if isinstance(categoryJsonData, dict):
                if chosenCategory in categoryJsonData and isinstance(categoryJsonData[chosenCategory], dict):
                    wordDataDict = categoryJsonData[chosenCategory]
                    selectedCategoryName = chosenCategory
                    categoryDescription = f"Words related to {chosenCategory}."
                else:
                    print(f"Warning: Unexpected JSON structure for category '{chosenCategory}' in {filePath}. Expected a dictionary under the category key.")
                    wordDataDict = {"HANGMAN": "A classic word guessing game."}
                    selectedCategoryName = "Default Words"
                    categoryDescription = "A general set of words."
            else:
                print(f"Warning: Unexpected top-level JSON structure in {filePath}. Expected a dictionary.")
                wordDataDict = {"HANGMAN": "A classic word guessing game."}
                selectedCategoryName = "Default Words"
                categoryDescription = "A general set of words."
        else:
            print(f"Warning: Category file not found: {filePath}. Using default words.")
        
        if not wordDataDict:
            wordDataDict = {"HANGMAN": "A classic word guessing game."}
            selectedCategoryName = "Default Words"
            categoryDescription = "A general set of words."
            QMessageBox.warning(self, "No Words Loaded", "No words found for selected categories or files are missing/invalid. Using default words.")
        
        return wordDataDict, selectedCategoryName, categoryDescription

    def display_word(self):
        return " ".join(letter if letter in self.guessedLetters else "_" for letter in self.secretWord)

    def make_guess(self):
        guess = self.guessInput.text().strip().upper()
        fullWordGuessingMode = self.settings.get("full_word_guessing", "Off")
        self.guessInput.clear()

        if not guess:
            return

        self.check_and_unlock_achievement("Achievement_Welcome")

        ## Full Word Guess
        if len(guess) > 1: 
            if fullWordGuessingMode == "Off":
                self.incorrectGuessesInRound += 1
                return
            elif not guess.isalpha(): ## Check for Real Letters
                self.check_and_unlock_achievement("Achievement_Alphabet")
                return
            if guess == self.secretWord:
                self.check_and_unlock_achievement("Achievement_Solve_Correct")
                if len(self.guessedLetters) == 0:
                    self.check_and_unlock_achievement("Achievement_Solve_Correct_No_Help")
                for letter in self.secretWord: ## Reveal all letters
                    self.guessedLetters.add(letter)
                self.wordLabel.setText(self.display_word())
                self.end_game(win=True)
            else:
                self.check_and_unlock_achievement("Achievement_Solve_Wrong")
                self.remainingAttempts -= 1
                self.incorrectGuessesInRound += 1
                self.update_status_label()
                self.update_hangman_image()
                if self.remainingAttempts == 0:
                    self.end_game(win=False)
                else:
                    QMessageBox.information(self, "Incorrect Word!", f"'{guess}' is not the word. You lost 1 attempt.")
        ## Single Letter Guess
        else:
            if guess == " ":
                return
            elif not guess.isalpha() and guess != " ": ## Check for Real Letters
                self.check_and_unlock_achievement("Achievement_Alphabet")
                QMessageBox.warning(self, "Invalid Input", "Please enter a letter from American Alphabet.")
                return

            elif guess in self.guessedLetters: ## Already Guessed
                self.check_and_unlock_achievement("Achievement_Same_Letter")
                QMessageBox.warning(self, "Already Guessed", f"You've already guessed '{guess}'.")
                return

            self.guessedLetters.add(guess)
            ## Disable Keyboard Button
            for button in self.keyboardFrame.findChildren(QPushButton):
                if button.text() == guess:
                    button.setDisabled(True)
                    break

            if guess in self.secretWord:
                self.wordLabel.setText(self.display_word())
                if "_" not in self.display_word():
                    self.end_game(win=True)
            else:
                self.remainingAttempts -= 1
                self.incorrectGuessesInRound += 1
                self.update_status_label()
                self.update_hangman_image()
                if self.remainingAttempts == 0:
                    self.end_game(win=False)

    def update_status_label(self):
        hintsMode = self.settings.get("hints_mode", "Auto")

        if hintsMode == "Always":
            self.statusLabel.setText(self.wordDataDict.get(self.secretWordDisplay, "Guess the hidden word!"))
        elif hintsMode == "Auto":
            halfStrikesLimit = self.initialStrikesLimit // 2
            if self.remainingAttempts <= halfStrikesLimit:
                self.statusLabel.setText(self.wordDataDict.get(self.secretWordDisplay, "Guess the hidden word!"))
            else:
                self.statusLabel.setText(f"Remaining Attempts: {self.remainingAttempts}")
        else:
            self.statusLabel.setText(f"Remaining Attempts: {self.remainingAttempts}")

    def update_hangman_image(self):
        maxAttempts = self.settings.get("strikes_limit", 6)

        ## Calculate Fraction of Attempts Taken
        strikesTaken = maxAttempts - self.remainingAttempts
        progress = strikesTaken / maxAttempts  # value between 0 and 1
        displayImageIndex = round(progress * 6)
        displayImageIndex = max(0, min(6, displayImageIndex))
        imagePath = resource_path(os.path.join("Data", f"hangman_{displayImageIndex}.jpg"))
        pixmap = QPixmap(imagePath)

        if os.path.exists(imagePath):
            pixmap.load(imagePath)
        else:
            ## Create a simple blank image if the specific hangman image is not found
            blankImage = QImage(200, 200, QImage.Format.Format_ARGB32)
            blankImage.fill(QColor(0, 0, 0, 0))
            pixmap = QPixmap.fromImage(blankImage)
            print(f"Warning: Hangman image not found: {imagePath}. Using a blank placeholder.")

        self.hangmanImage.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def give_up(self):
        reply = QMessageBox.question(self, "Give Up?",
                                     "Are you sure you want to give up? The word will be revealed.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.wordLabel.setText(self.secretWord)
            self.end_game(win=False)
        else:
            pass

    def open_menu(self):
        self.check_and_unlock_achievement("Achievement_Stop_Playing")
        if len(self.guessedLetters) > 0:
            self.check_and_unlock_achievement("Achievement_Terminate")
        self.switch_window("MainMenuWindow")

    def end_game(self, win):
        totalCompletedWords = self.unlockedData["unlockedAchievementsProgress"].get("Achievement_All_Topics", 0)
        self.unlockedData["unlockedAchievementsProgress"]["Achievement_All_Topics"] = (totalCompletedWords + 1)

        ## Win Game
        if win:
            self.check_and_unlock_achievement("Achievement_Winner")

            if self.remainingAttempts == 1:
                self.check_and_unlock_achievement("Achievement_Close_Call")

            if self.settings.get("hints_mode", "Auto") == "Never":
                self.check_and_unlock_achievement("Achievement_Hard_Mode")

            ## Update Win Count and Unique Words Guessed
            if "unique_words_guessed" not in self.unlockedData:
                self.unlockedData["unique_words_guessed"] = []

            self.unlockedData["win_count"] = self.unlockedData.get("win_count", 0) + 1
            if self.secretWord not in self.unlockedData.get("unique_words_guessed", []):
                self.unlockedData["unique_words_guessed"].append(self.secretWord)

            ## Add Word to Completed Words
            completedInCategory = self.completedWords.get(self.currentDLCTheme, [])
            if self.secretWord not in completedInCategory:
                if self.currentDLCTheme not in self.completedWords:
                    self.completedWords[self.currentDLCTheme] = []
                self.completedWords[self.currentDLCTheme].append(self.secretWord)
                save_json(self.completedWordsPath, self.completedWords)

                ## Get the New Completed Count for the Current Category
                newCompletedCount = len(self.completedWords.get(self.currentDLCTheme, []))
                
                ## Achievement Progress Update
                match self.currentDLCTheme:
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

                currentProgress = self.unlockedData["unlockedAchievementsProgress"].get(achievementThemeName, 0)
                print(f"Current progress for {achievementThemeName}: {currentProgress}, New completed count: {newCompletedCount}")
                
                ## Update Progress if Higher
                if newCompletedCount > currentProgress:
                    self.unlockedData["unlockedAchievementsProgress"][achievementThemeName] = newCompletedCount
                    
        ## Save and Check Achievements
        self.check_and_unlock_achievement()
        save_json(self.unlockedAchievementsPath, self.unlockedData)

        self.guessInput.setDisabled(True)
        self.guessButton.setDisabled(True)
        self.giveUpButton.setDisabled(True)
        for button in self.keyboardFrame.findChildren(QPushButton):
            button.setDisabled(True)
        self.restartButton.show()

    def restart_game(self):
        self.refresh_data_from_files()
        self.apply_settings()
        self.incorrectGuessesInRound = 0
        self.guessedLetters = set()
        self.remainingAttempts = self.settings.get("strikes_limit", 6)

        ## Load Words from Enabled Categories
        self.wordDataDict, self.currentDLCTheme, self.currentDLCDescription = self.load_words()
        completedCurrentCategory = self.completedWords.get(self.currentDLCTheme, [])
        availableWords = [word for word in self.wordDataDict.keys() if word not in completedCurrentCategory]

        if availableWords:
            self.secretWordDisplay = random.choice(availableWords)
            self.secretWord = self.secretWordDisplay.upper()
        else:
            self.secretWord = "HANGMAN"
            self.currentDLCTheme = "Default Words"
            self.currentDLCDescription = "A general set of words (all words completed in enabled categories)."
            QMessageBox.information(self, "No New Words", "All words in the enabled categories have been completed! Playing with a default word. You can reset game history in settings to play them again.")

        ## Automatically Reveal These Characters
        for char in self.secretWord:
            if char == ' ':
                self.guessedLetters.add(' ')
            if char == ',':
                self.guessedLetters.add(',')

        self.wordLabel.setText(self.display_word())
        self.update_status_label()
        self.DLCThemeLabel.setText(self.currentDLCTheme)

        self.guessInput.setDisabled(False)
        self.guessButton.setDisabled(False)
        self.giveUpButton.setDisabled(False)
        self.restartButton.hide()

        ## Enable Keyboard Buttons
        for button in self.keyboardFrame.findChildren(QPushButton):
            button.setDisabled(False)
        
        self.update_hangman_image()

    def check_and_unlock_achievement(self, unlockName=None):
        ## Check Every Achievement
        for achievementId, achievementsList in self.allAchievements.items():
            if achievementsList:
                achievement = achievementsList[0]
            
                ## Skip Unlocked Achievements
                if achievementId in self.unlockedData.get("unlockedAchievements", []):
                    continue

                unlocked = False
                tracker = achievement.get("AchievementProgressTracker")

                if achievementId == unlockName and unlockName != None:
                    unlocked = True

                # Handle Tracker Achievements
                elif isinstance(tracker, int):
                    currentProgress = self.unlockedData["unlockedAchievementsProgress"].get(achievementId, 0)
                    if currentProgress >= tracker:
                        unlocked = True

                if unlocked:
                    self.unlock_achievement(achievementId, achievement.get("Name"), achievement.get("Description"))
    
    def unlock_achievement(self, achievementId, title, description):
        if achievementId not in self.unlockedData.get("unlockedAchievements", []):
            self.unlockedData["unlockedAchievements"].append(achievementId)
            self.unlockedData["unlockTimes"][achievementId] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            save_json(self.unlockedAchievementsPath, self.unlockedData)
        
            self.show_achievement_popup(achievementId, title, description)

    def show_achievement_popup(self, achievementId, title, description):
        iconPath = resource_path(os.path.join("Achievement Icons", achievementId + ".png"))
        popupHtml = f"""
        <div style="display: flex; align-items: flex-start;">
            <img src="{iconPath}" width="48" height="48" style="margin-right: 10px;">
            <div>
                <div style="font-weight: bold; font-size: 14pt;">{title}</div>
                <div style="font-size: 10pt; color: #555;">{description}</div>
            </div>
        </div>
        """
        self.achievementPopup.setText(popupHtml)
        self.achievementPopup.adjustSize()

        ## Position bottom right
        self.achievementPopup.move(
            self.width() - self.achievementPopup.width() - 20,
            self.height() - self.achievementPopup.height() - 20
        )
        self.achievementPopup.show()
        self.achievementTimer.start(5000)

    def hide_achievement_popup(self):
        self.achievementPopup.hide()
        self.achievementTimer.stop()

    def resizeEvent(self, event):
        self.backgroundImage.setGeometry(0, 0, self.width(), self.height())
        if not self.achievementPopup.isHidden():
            self.achievementPopup.move(
                self.width() - self.achievementPopup.width() - 20,
                self.height() - self.achievementPopup.height() - 20
            )
        super().resizeEvent(event)