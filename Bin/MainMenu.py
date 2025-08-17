from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QRect, Qt
import os, sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainMenu(QWidget):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window  

        # Background Image
        self.backgroundImage = QLabel(self)
        self.backgroundImage.setPixmap(QPixmap(resource_path(os.path.join("Data", "woodBackground.jpg"))))
        self.backgroundImage.setScaledContents(True)
        self.backgroundImage.setGeometry(0, 0, self.width(), self.height())

        # Create Overylay
        self.overlay = QWidget(self)
        self.overlay.setGeometry(QRect(0, 0, self.width(), self.height()))
        self.overlayLayout = QVBoxLayout(self.overlay)
        self.overlay.setLayout(self.overlayLayout)

        # Title Label
        titleLayout = QLabel("Hangman Game", self.overlay)
        titleLayout.setStyleSheet("color: white; font-size: 48px;")
        titleLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlayLayout.addWidget(titleLayout)

        # Hangman Image
        hangmanImage = QLabel(self.overlay)
        hangmanImage.setPixmap(QPixmap(resource_path(os.path.join("Data", "hangmanImage.jpg"))))
        hangmanImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlayLayout.addWidget(hangmanImage)

        # Button Style
        buttonStyle = """
            QPushButton {
                background-color: #444;
                color: white;
                font-size: 18px;
                padding: 5px;
                border-radius: 10px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: #666;
                border: 2px solid #2997ff;
            }
        """

        # Menu Buttons
        playButton = QPushButton("Play Game", self.overlay)
        playButton.setStyleSheet(buttonStyle)
        playButton.clicked.connect(self.playGame)
        self.overlayLayout.addWidget(playButton)

        #createWordButton = QPushButton("Create Words", self.overlay)
        #createWordButton.setStyleSheet(buttonStyle)
        #createWordButton.clicked.connect(lambda: self.switch_window("CreateWordsWindow"))
        #self.overlayLayout.addWidget(createWordButton)

        achievementsButton = QPushButton("Achievements", self.overlay)
        achievementsButton.setStyleSheet(buttonStyle)
        achievementsButton.clicked.connect(lambda: self.switch_window("AchievementsWindow", restart=True))
        self.overlayLayout.addWidget(achievementsButton)

        settingsButton = QPushButton("Settings", self.overlay)
        settingsButton.setStyleSheet(buttonStyle)
        settingsButton.clicked.connect(lambda: self.switch_window("SettingsWindow"))
        self.overlayLayout.addWidget(settingsButton)

        quitButton = QPushButton("Quit", self.overlay)
        quitButton.setStyleSheet(buttonStyle)
        quitButton.clicked.connect(QApplication.quit)
        self.overlayLayout.addWidget(quitButton)

        self.overlay.raise_()

    def playGame(self):
        self.switch_window("GameWindow", restart=True)

    def resizeEvent(self, event):
        self.backgroundImage.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)