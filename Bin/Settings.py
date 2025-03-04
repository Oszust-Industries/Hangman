from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QSpinBox, QComboBox, QPushButton, QScrollArea, QWidget, QGroupBox, QFormLayout, QHBoxLayout

class SettingsWindow(QDialog):
    def __init__(self, switchWindowCallback):
        super().__init__()

        self.switchWindow = switchWindowCallback

        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 350, 500)

        # Main layout
        layout = QVBoxLayout()

        # Scrollable area setup
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget()
        scrollLayout = QVBoxLayout(scrollContent)

        ### Gameplay Settings
        gameplayBox = QGroupBox("Gameplay Settings")
        gameplayLayout = QVBoxLayout()

        # On-Screen Keyboard
        self.keyboardCheckbox = QCheckBox("Enable On-Screen Keyboard")
        gameplayLayout.addWidget(self.keyboardCheckbox)

        # Hints Mode (Auto, Always, Never)
        self.hintsCombo = QComboBox()
        self.hintsCombo.addItems(["Auto", "Always", "Never"])
        gameplayLayout.addWidget(self.labeledWidget("Hints Mode:", self.hintsCombo))

        # Full Word Guessing (Auto, Always, Never)
        self.guessCombo = QComboBox()
        self.guessCombo.addItems(["Auto", "Always", "Never"])
        gameplayLayout.addWidget(self.labeledWidget("Full Word Guessing:", self.guessCombo))

        # Strikes Limit
        self.strikesSpinbox = QSpinBox()
        self.strikesSpinbox.setRange(3, 10)
        self.strikesSpinbox.setValue(6)
        gameplayLayout.addWidget(self.labeledWidget("Strikes Limit:", self.strikesSpinbox))

        gameplayBox.setLayout(gameplayLayout)
        scrollLayout.addWidget(gameplayBox)

        ### Audio Settings
        audioBox = QGroupBox("Audio Settings")
        audioLayout = QVBoxLayout()
        self.soundCheckbox = QCheckBox("Enable Sound Effects")
        audioLayout.addWidget(self.soundCheckbox)
        audioBox.setLayout(audioLayout)
        scrollLayout.addWidget(audioBox)

        ### Accessibility Settings
        accessibilityBox = QGroupBox("Accessibility Settings")
        accessibilityLayout = QVBoxLayout()
        self.fontSizeCombo = QComboBox()
        self.fontSizeCombo.addItems(["Small", "Medium", "Large"])
        self.highContrastCheckbox = QCheckBox("Enable High Contrast Mode")
        accessibilityLayout.addWidget(self.labeledWidget("Font Size:", self.fontSizeCombo))
        accessibilityLayout.addWidget(self.highContrastCheckbox)
        accessibilityBox.setLayout(accessibilityLayout)
        scrollLayout.addWidget(accessibilityBox)

        ### Categories & DLC Selection
        categoryBox = QGroupBox("Categories & DLC")
        categoryLayout = QVBoxLayout()
        self.categories = {
            "Animals": QCheckBox("Animals"),
            "Movies": QCheckBox("Movies"),
            "Science": QCheckBox("Science"),
            "Sports": QCheckBox("Sports"),
            "Fantasy DLC": QCheckBox("Fantasy DLC"),
            "History DLC": QCheckBox("History DLC"),
        }

        for cb in self.categories.values():
            categoryLayout.addWidget(cb)

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

        self.setLayout(layout)

    def labeledWidget(self, _, widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(widget)
        return container

    def saveAndClose(self):
        self.switchWindow("MainMenuWindow")
        self.close()

    def resetAchievements(self):
        print("Achievements Reset")

    def resetHistory(self):
        print("Game History Reset")

    def resetSettings(self):
        self.keyboardCheckbox.setChecked(False)
        self.hintsCombo.setCurrentIndex(0)
        self.guessCombo.setCurrentIndex(0)
        self.soundCheckbox.setChecked(False)
        self.strikesSpinbox.setValue(6)
        self.fontSizeCombo.setCurrentIndex(1)
        self.highContrastCheckbox.setChecked(False)
        for cb in self.categories.values():
            cb.setChecked(False)
        print("Settings Reset")

