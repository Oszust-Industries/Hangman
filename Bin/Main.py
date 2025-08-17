## Hangman Game - Oszust Industries
## Created on: 2-11-25 - Last update: 8-17-25
softwareVersion = "v1.0.0"
systemName, systemBuild = "Hangman", "dev"
import json, os, sys
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QStackedWidget
import MainMenu, Hangman, Achievements, Settings

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class GameSetup:
    def fileSetup():
        basePath = os.path.join(os.getenv('APPDATA'), 'Oszust Industries')
        hangmanPath = os.path.join(basePath, 'Hangman Game')
        ## Create Appdata Folders
        os.makedirs(hangmanPath, exist_ok=True)
        ## Create Achievement Save
        if os.path.exists(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'unlockedAchievements.json')) == False:
            defaultData = {"unlockedAchievements": [], "unlockedAchievementsProgress": {}, "unlockTimes": {}, "win_count": 0, "unique_words_guessed": []}
            with open(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'unlockedAchievements.json'), 'w') as json_file:
                json.dump(defaultData, json_file, indent=4)

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.MainMenuWindow = MainMenu.MainMenu(self.switchWindow)
        self.GameWindow = Hangman.GameWindow(self.switchWindow)
        self.SettingsWindow = Settings.SettingsWindow(self.switchWindow)
        self.AchievementsWindow = Achievements.AchievementsWindow(self.switchWindow)

        self.addWidget(self.MainMenuWindow)
        self.addWidget(self.GameWindow)
        self.addWidget(self.SettingsWindow)
        self.addWidget(self.AchievementsWindow)

        self.setWindowIcon(QtGui.QIcon(resource_path(os.path.join("Data", "icon.png"))))

        self.setWindowTitle("Hangman")
        self.setMinimumSize(800, 500)
        self.setCurrentWidget(self.MainMenuWindow)

    def switchWindow(self, windowName, restart=False):
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
    GameSetup.fileSetup()

    game = QApplication(sys.argv)
    hangmanGame = MainApp()
    hangmanGame.show()
    sys.exit(game.exec())