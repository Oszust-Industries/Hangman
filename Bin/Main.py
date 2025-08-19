## Hangman Game - Oszust Industries
## Created on: 2-11-25 - Last update: 8-18-25
softwareVersion = "v1.0.0"
systemName, systemBuild = "Hangman", "dev"

from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6 import QtGui
import MainMenu, Hangman, Achievements, Settings
import json, os, sys

def resource_path(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

class GameSetup:
    def file_setup():
        basePath = os.path.join(os.getenv('APPDATA'), 'Oszust Industries')
        hangmanPath = os.path.join(basePath, 'Hangman Game')
        ## Create Appdata Folders
        os.makedirs(hangmanPath, exist_ok=True)
        ## Create Achievement Save
        if os.path.exists(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'unlockedAchievements.json')) == False:
            defaultData = {"unlockedAchievements": [], "unlockedAchievementsProgress": {}, "unlockTimes": {}}
            with open(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'unlockedAchievements.json'), 'w') as json_file:
                json.dump(defaultData, json_file, indent=4)
        ## Create Completed Words
        if os.path.exists(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'completedWords.json')) == False:
            defaultData = {"unique_words": [], "unique_words_correct": []}
            with open(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'completedWords.json'), 'w') as json_file:
                json.dump(defaultData, json_file, indent=4)

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.MainMenuWindow = MainMenu.MainMenu(self.switch_window)
        self.GameWindow = Hangman.GameWindow(self.switch_window)
        self.SettingsWindow = Settings.SettingsWindow(self.switch_window)
        self.AchievementsWindow = Achievements.AchievementsWindow(self.switch_window)

        self.addWidget(self.MainMenuWindow)
        self.addWidget(self.GameWindow)
        self.addWidget(self.SettingsWindow)
        self.addWidget(self.AchievementsWindow)

        self.setWindowIcon(QtGui.QIcon(resource_path(os.path.join("Data", "icon.png"))))

        self.setWindowTitle("Hangman")
        self.setMinimumSize(800, 500)
        self.setCurrentWidget(self.MainMenuWindow)

    def switch_window(self, windowName, restart=False):
        windows = {
            "MainMenuWindow": self.MainMenuWindow,
            "GameWindow": self.GameWindow,
            "SettingsWindow": self.SettingsWindow,
            "AchievementsWindow": self.AchievementsWindow,
        }
        if windowName in windows:
            if windowName == "GameWindow" and restart:
                self.GameWindow.restart_game()
            elif windowName == "AchievementsWindow" and restart:
                self.AchievementsWindow.reloadAchievements()
            self.setCurrentWidget(windows[windowName])

if __name__ == "__main__":
    GameSetup.file_setup()

    game = QApplication(sys.argv)
    hangmanGame = MainApp()
    hangmanGame.show()
    sys.exit(game.exec())