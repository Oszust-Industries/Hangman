import json, os, sys
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea, QFrame, QProgressBar, QPushButton, QSpacerItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def loadJson(filePath, default=None):
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{filePath}': {e}")
        return default if default is not None else {}

class AchievementsWindow(QWidget):
    def __init__(self, switchWindowCallback):
        super().__init__()
        self.switchWindowCallback = switchWindowCallback
        self.setWindowTitle("Achievements")

        # Main Layout
        mainLayout = QVBoxLayout(self)

        # Load achievements and unlocked data
        self.achievements = loadJson(resource_path(os.path.join("Data", "Achievements.json")))
        self.unlockedData = loadJson(os.path.join(os.getenv('APPDATA'), 'Oszust Industries', 'Hangman Game', 'unlockedAchievements.json'), {})
        
        # Calculate total and unlocked achievements
        totalAchievements = sum(len(achList) for achList in self.achievements.values())
        unlockedAchievements = len(self.unlockedData.get("unlockedAchievements", []))
        
        # Progress Bar Layout
        progressLayout = QVBoxLayout()
        progressLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(totalAchievements)
        self.progressBar.setValue(unlockedAchievements)
        self.progressBar.setTextVisible(True)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setFormat(f"{unlockedAchievements} / {totalAchievements} Achievements")
        self.progressBar.setFixedWidth(500)
        self.progressBar.setStyleSheet("""
            QProgressBar {background-color: #333; height: 12px; border-radius: 6px; color: white;}
            QProgressBar::chunk {background-color: #2997ff; border-radius: 6px;}""")
        
        progressLayout.addWidget(self.progressBar)
        mainLayout.addLayout(progressLayout)

        # Scrollable Area for Achievements
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget()
        self.layout = QVBoxLayout(scrollContent)
        scrollArea.setWidget(scrollContent)
        mainLayout.addWidget(scrollArea)

        # Load achievements and unlocked data
        self.displayAchievements()

        spacer = QSpacerItem(20, 40)
        self.layout.addItem(spacer)

        # Fixed bottom button container
        self.buttonContainer = QWidget()
        self.buttonLayout = QHBoxLayout(self.buttonContainer)

        # Add Close button
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.closeButtonClicked)
        self.buttonLayout.addWidget(self.closeButton)
        mainLayout.addWidget(self.buttonContainer)

        self.setLayout(mainLayout)

    def displayAchievements(self):
        achievementsMeta = self.achievements
        unlocked = self.unlockedData.get("unlockedAchievements", [])
        unlockedProgress = self.unlockedData.get("unlockedAchievementsProgress", {})

        # Group achievements by DLC
        dlcGroups = {}
        for keyName in achievementsMeta.keys():
            achievementList = achievementsMeta[keyName]

            for achievement in achievementList:
                dlcName = achievement.get("DLC", "Base")
            
                if dlcName not in dlcGroups:
                    dlcGroups[dlcName] = []

                dlcGroups[dlcName].append((keyName, achievement))

        # DLC Groups
        for dlcName, achievements in dlcGroups.items():
            if dlcName == "Base": 
                dlcHeader = QLabel(f"Hangman:")
            else:
                dlcHeader = QLabel(f"{dlcName} DLC:")
            dlcHeader.setStyleSheet("font-weight: bold; color: white; font-size: 16px; margin-top: 20px;")
            self.layout.addWidget(dlcHeader)

            # Add Achievements
            for keyName, achievement in achievements:
                isUnlocked = keyName in unlocked
                progressGoal = achievement.get("AchievementProgressTracker")
                progressValue = unlockedProgress.get(keyName, 0)

                # Achievement Box
                achievementBox = QFrame()
                achievementBox.setStyleSheet("background-color: #2A2A2E; border-radius: 8px; padding: 8px;")
                achievementLayout = QHBoxLayout(achievementBox)
                achievementLayout.setSpacing(10)

                # Load Achievement Image
                if isUnlocked:
                    imageFilename = resource_path(os.path.join("Data", "Achievement Icons", f"{keyName}.png"))
                else:
                    imageFilename = resource_path(os.path.join("Data", "Achievement Icons", f"{keyName}_locked.png"))

                imageLabel = QLabel()
                if os.path.exists(imageFilename):
                    pixmap = QPixmap(imageFilename)
                else:
                    default_image_path = resource_path(os.path.join("Data", "Achievement Icons", "default.png"))
                    pixmap = QPixmap(default_image_path)

                imageLabel.setPixmap(pixmap)
                achievementLayout.addWidget(imageLabel)

                textLayout = QVBoxLayout()
                textLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                textLayout.setSpacing(2)

                # Achievement Title
                if achievement.get("Hidden", False) and not isUnlocked:
                    titleLabel = QLabel("Hidden Achievement")
                    titleLabel.setStyleSheet("font-weight: bold; color: white; font-size: 32px;" if isUnlocked else "color: gray;")
                else:
                    titleLabel = QLabel(achievement.get("Name", "Unknown Achievement"))
                    titleLabel.setStyleSheet("font-weight: bold; color: white; font-size: 32px;" if isUnlocked else "color: gray;")
                textLayout.addWidget(titleLabel)

                # Achievement Description
                if achievement.get("Hidden", False) and not isUnlocked:
                    descriptionLabel = QLabel("???")
                    descriptionLabel.setStyleSheet("color: lightgray; font-size: 12px;")
                else:
                    descriptionLabel = QLabel(achievement.get("Description", "No description available"))
                    descriptionLabel.setStyleSheet("color: lightgray; font-size: 12px;")
                textLayout.addWidget(descriptionLabel)

                achievementLayout.addLayout(textLayout, 1)

                # Progress Bar / Unlock Time
                progressLayout = QHBoxLayout()
                progressLayout.setAlignment(Qt.AlignmentFlag.AlignRight)

                if isUnlocked: # Unlock Time
                    unlockDatetime = datetime.strptime(self.unlocked_data.get("unlockTimes", {}).get(keyName, "Unknown Time"), "%Y-%m-%d %H:%M:%S.%f")

                    if unlockDatetime.date() == datetime.now().date():
                        formattedTime = f"Today at {unlockDatetime.strftime('%I:%M %p').lstrip('0')}"
                    elif unlockDatetime.date() == (datetime.now() - timedelta(days=1)).date():
                        formattedTime = f"Yesterday at {unlockDatetime.strftime('%I:%M %p').lstrip('0')}"
                    else:
                        formattedTime = unlockDatetime.strftime("%B %d, %Y at %I:%M %p").replace(" 0", " ")

                    unlockLabel = QLabel(f"Unlocked: {formattedTime}")
                    unlockLabel.setStyleSheet("color: lightgray; font-size: 12px;")
                    progressLayout.addWidget(unlockLabel)
                else:  # Progress Bar
                    if progressGoal:
                        progressBar = QProgressBar()
                        progressBar.setMinimum(0)
                        progressBar.setMaximum(progressGoal)
                        progressBar.setValue(progressValue)
                        progressBar.setTextVisible(False)
                        progressBar.setFixedWidth(180)
                        progressBar.setStyleSheet("""
                            QProgressBar {background-color: #333; height: 8px;}
                            QProgressBar::chunk {background-color: #2997ff;}""")

                        progressLabel = QLabel(f"{progressValue} / {progressGoal}")
                        progressLabel.setStyleSheet("color: lightgray; font-size: 12px;")
                        progressLayout.addWidget(progressBar)
                        progressLayout.addWidget(progressLabel)

                achievementLayout.addLayout(progressLayout)

                self.layout.addWidget(achievementBox)

    def closeButtonClicked(self):
        self.switchWindowCallback("MainMenuWindow")
