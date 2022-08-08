## Hangman Game - Oszust Industries
## Created on: 5-10-21 - Last update: 10-01-21
## Achievement Notifications Library v1.4.5 - Oszust Industries
gameVersion = "v1.4.2"
newestAchievementVersion = "v1.4.5"
from datetime import date, datetime, timedelta
import os
import pickle
import random
import time

def gameConfig():
## System Configures
    global deactivateFileOpening, enableAccountSystem, enableAchievementThreading, exitSystem, overrideResetAchivements, resetSettings, systemName
    systemName = "Hangman"
    exitSystem = False
## Change Configures
    resetSettings = False
    ## V|WARNING|: No Playtime/Achievements Saved
    overrideResetAchivements = False
    enableAchievementThreading = True
    deactivateFileOpening = False
    enableAccountSystem = True

def gameSetup():
## Setup Game
    global accountReady, allWordsUsed, availablePossibleAnswers, oneGamePlayed, usedWordList
    print("Loading...")
    accountReady = False
    allWordsUsed = False
    availablePossibleAnswers = []
    oneGamePlayed = False
    usedWordList = []
## Start Functions
    gameConfig()
    clear()
    print("Welcome to Hangman. " + gameVersion + "\nCreated and published by Oszust Industries\n\n\nOszust Industries Login System:\n\n")
    accountLogin("setup")
    if exitSystem == False:
        Achievements("setup")
        accountReady = True
        startMenu("")

def accountLogin(accountAction):
## Save User Settings
    from random import randrange
    import math
    import shutil
    global account2Way, accountActiveOwnedDLC, accountEmail, accountInput, accountLanguage, accountOwnedDLC, accountPassword, availableAccounts, availablePossibleAnswers, currentAccountInfoPath, currentAccountPath, currentAccountUsername, deactivateFileOpening, emailCode, emailExpireTime, emailconfirmed, enableAccountSystem, exitSystem, expiredCodes, gameHintsActivated, lockDateTime, packedAccountGames, packedAccountInformation, packedSettings, passwordAttemptsLeft, punishmentMode, resetAchievements, smartWordDetector, startedCreateAccount, tempAvailableAccounts, win10ToastActive
    weakPasswords = ["1234", "password", "forgot password", "forgotpassword", "default", "incorrect", "back", "quit", "return", "logout"]
    badUsernames = ["disneyhockey40", "guest", "default", ""]
## Account Setup
    if accountAction == "setup":
        lockDateTime = ""
        expiredCodes = []
        emailconfirmed = False
        passwordAttemptsLeft = 5
        currentAccountUsername = ""
## Windows Detector
        if os.name != "nt": deactivateFileOpening = True
        accountLogin("createUserPath")
        if deactivateFileOpening == False:
            try:
                availableAccounts = pickle.load(open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Available Account.p"), "rb"))
                availableAccounts.sort()
            except OSError: availableAccounts = []
        else:
            availableAccounts = []
            enableAccountSystem = False
        if enableAccountSystem == False:
            currentAccountUsername = "Default"
            if deactivateFileOpening == False:
                currentAccountInfoPath = str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername)
                currentAccountPath = (currentAccountInfoPath + "\\" + systemName)
            else:
                currentAccountInfoPath = ""
                currentAccountPath = ""
            try: packedAccountGames = pickle.load(open(currentAccountInfoPath + "\\accountGames.p", "rb"))
            except OSError: accountLogin("createUserPath")
            accountLogin("readSettings")
            return
        tempAvailableAccounts = availableAccounts
        if "Default" in availableAccounts:
            tempAvailableAccounts = tempAvailableAccounts.remove("Default")
            if len(availableAccounts) <= 1: tempAvailableAccounts = []
        if len(tempAvailableAccounts) > 0:
            print("Available Accounts:")
            for i in tempAvailableAccounts:
                if i != "Default": print(str(tempAvailableAccounts.index(i) + 1) + ". " + i)
        else: print("No Available Accounts:")
        print("\n" + str(len(tempAvailableAccounts) + 1) + ". Add account")
        print(str(len(tempAvailableAccounts) + 2) + ". Login as guest")
        if len(tempAvailableAccounts) > 0: print(str(len(tempAvailableAccounts) + 3) + ". Remove account")
        if len(tempAvailableAccounts) > 0: print(str(len(tempAvailableAccounts) + 4) + ". Quit")
        else: print(str(len(tempAvailableAccounts) + 3) + ". Quit")
        accountInput = input("\nType the account number to login. ").replace(" ", "")
        if accountInput.isnumeric() or accountInput in availableAccounts:
            if int(accountInput) == len(tempAvailableAccounts) + 1:
                clear()
                startedCreateAccount = False
                accountLogin("createAccount_1")
            elif int(accountInput) == len(tempAvailableAccounts) + 2:
                print("\n\nLoading Account...")
                deactivateFileOpening = True
                win10ToastActive = False
                gameHintsActivated = True
                smartWordDetector = True
                punishmentMode = False
                currentAccountUsername = "Guest"
                accountLogin("readOwnedDLC")
                clear()
            elif int(accountInput) == len(tempAvailableAccounts) + 3 and len(tempAvailableAccounts) > 0:
                clear()
                accountLogin("deleteAccount")
            elif int(accountInput) == len(tempAvailableAccounts) + 3 and len(tempAvailableAccounts) <= 0:
                    accountLogin("quit")
            elif int(accountInput) == len(tempAvailableAccounts) + 4 and len(tempAvailableAccounts) > 0:
                    accountLogin("quit")
            elif (int(accountInput) < len(tempAvailableAccounts) + 1 and int(accountInput) > 0) or accountInput in availableAccounts:
                if accountInput.isnumeric(): currentAccountUsername = availableAccounts[int(accountInput) - 1]
                else: currentAccountUsername = accountInput
                currentAccountInfoPath = str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername)
                currentAccountPath = (currentAccountInfoPath + "\\" + systemName)
                accountLogin("readSettings")
            else:
                clear()
                print("You typed an unavailable account number.\n\n\n")
                accountLogin("setup")
        else:
            clear()
            print("You typed an unavailable account number.\n\n\n")
            accountLogin("setup")
## Account Logout
    elif accountAction == "logout":
        if exitSystem == False:
            exitSystem = True
            print("\n\n\nDo not close application.\nSaving and logging out...\n")
        if currentAccountUsername != "":
            Achievements("saving")
            if len(waitingAchievementsList) <= 0: gameSetup()
            else:
                time.sleep(0.3)
                accountLogin("logout")
## Account Quit
    elif accountAction == "quit":
        print("\n\n\nDo not close application.\nSaving and exiting...\n")
        exitSystem = True
        if currentAccountUsername != "": Achievements("saving")
## Email
    elif "emailAccount" in accountAction:
        if deactivateFileOpening == False:
            print("Loading verification system...")
            import smtplib
            systemEmail = "noreply.oszustindustries@gmail.com"
            oo7 = pickle.load(open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Data.p"), "rb"))
            emailMessage = str(accountAction.replace("emailAccount_", ""))
            to = [accountEmail]
            if emailMessage == "resetPasswordCode":
                subject = "Manage Password Code"
                body = "Below is the code to manage the password for your Oszust Industries account:\n\n" + str(emailCode) + "\n\nThis code expires in 5 minutes.\n\n\nOszust Industries (no-reply)"
            elif emailMessage == "verificationCode":
                subject = "Verification Code"
                body = "Below is the code to login into your Oszust Industries account:\n\n""" + str(account2Way) + "\n\nThis code expires in 5 minutes.\n\n\nOszust Industries (no-reply))"
            message = 'Subject: {}\n\n{}'.format(subject, body)
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(systemEmail, oo7)
            smtp_server.sendmail(systemEmail, to, message)
            emailExpireTime = datetime.now() + timedelta(minutes=5)
            smtp_server.close()
            print("\nBe sure to check your junk mail for the email.\n")
## Create Account
    elif "createAccount" in accountAction:
        createAccountStep = int(accountAction.replace("createAccount_", ""))
        if createAccountStep == 1:
            if startedCreateAccount == False: print("Create Account:\n\nType 'back' to return to the previous prompt.\nType 'cancel' to cancel create account.")
            currentAccountUsername = input(str("\n\n\nA username is your name that you will select when logging into the server.\n\nWhat username would you like for your account? "))
            startedCreateAccount = True
            if currentAccountUsername.lower() in ["cancel", "quit", "exit", "back", "return"]: gameSetup()
            elif currentAccountUsername not in availableAccounts:
                if currentAccountUsername.lower().replace(" ", "") not in badUsernames: accountLogin("createAccount_2")
                else:
                    print("\nThis username is unavailable.")
                    accountLogin("createAccount_1")
            else:
                print("\nThis username is already in use.")
                accountLogin("createAccount_1")
        elif createAccountStep == 2:
            accountPassword = ""
            accountLanguage = "english"
            accountLogin("createAccount_3")
        elif createAccountStep == 3:
            accountEmail = input(str("\n\n\n\nAn email is required strictly for when you forget your password or a verification code needs to be sent.\n\nWhat email would you like to use for your account? ")).replace(" ", "")
            if accountEmail.lower() in ["cancel", "quit", "exit"]: gameSetup()
            elif accountEmail.lower() in ["back", "return"]: accountLogin("createAccount_1")
            elif "@" in accountEmail and "." in accountEmail: accountLogin("createAccount_4")
            else:
                print("\nThis email is not a valid email.")
                accountLogin("createAccount_3")
        elif createAccountStep == 4:
            if accountPassword == "": accountInput = input(str("\n\n\n\nA password will add more security to your account. The password will be required whenever an account action needs to take place.\n\nWould you like a password on your account? (yes/no) ")).replace(" ", "")
            else: accountInput = "yes"
            if accountInput.lower() in ["cancel", "quit", "exit"]: gameSetup()
            elif accountInput.lower() in ["back", "return"]: accountLogin("createAccount_3")
            elif accountInput.lower() in ["y", "yes"]:
                accountLogin("createAccount_5")
            elif accountInput.lower() in ["n", "no"]:
                accountPassword = "none"
                accountLogin("createAccount_6")
            else:
                print("\nPlease type yes or no.")
                accountLogin("createAccount_4")
        elif createAccountStep == 5:
            accountPassword = input(str("\nWhat password would you like for your account? "))
            if accountPassword.lower() in ["cancel", "quit", "exit"]: gameSetup()
            elif accountPassword.lower() in ["back", "return"]:
                accountPassword = ""
                accountLogin("createAccount_4")
            elif len(accountPassword) < 5:
                print("\n\n\nYour password needs to be at least five characters long.")
                accountLogin("createAccount_5")
            elif accountPassword.lower() in weakPasswords:
                print("\n\n\nYour password is too weak. Create a more unique password.")
                accountLogin("createAccount_5")
            else: accountLogin("createAccount_6")
        elif createAccountStep == 6:
            if accountPassword == "": print("\n\n\n\n2 factor verification will add more security to your account. This will be used whenever an account action needs to take place.")
            elif accountPassword != "": print("\n\n\n\n2 factor verification will add even more security to your account. This will be used with your password whenever an account action needs to take place.")
            accountInput = input(str("\n2 factor verification will email you a code to type in when it is required.\n\nWould you like 2 factor verification on your account? (yes/no) ")).replace(" ", "")
            if accountInput.lower() in ["cancel", "quit", "exit"]: gameSetup()
            elif accountInput.lower() in ["back", "return"]:
                accountPassword = ""
                accountLogin("createAccount_4")
            elif accountInput.lower() in ["y", "yes"]:
                account2Way = "active"
                accountLogin("createAccount_7")
            elif accountInput.lower() in ["n", "no"]:
                account2Way = "none"
                accountLogin("createAccount_7")
            else:
                print("\nPlease type yes or no.")
                accountLogin("createAccount_6")
        elif createAccountStep == 7:
            print("\n\n\n\n\n" + ("-" * 50) + "\nAccount Confirmation:" + "\n\n\nAccount username: " + currentAccountUsername + "\nAccount language: " + accountLanguage + "\nAccount email: " + accountEmail)
            if accountPassword != "none": print("Account password: Active")
            else: print("Account password: Inactive")
            if account2Way != "none": print("Account 2 factor verification: Active")
            else: print("Account 2 factor verification: Inactive")
            accountInput = input(str("\nDo these account details look right? (yes/no) ")).replace(" ", "")
            if accountInput.lower() in ["back", "return"]: accountLogin("createAccount_6")
            elif accountInput.lower() in ["y", "yes"]:
                availableAccounts.append(currentAccountUsername)
                pickle.dump(availableAccounts, open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Available Account.p"), "wb"))
                packedAccountInformation = [currentAccountUsername, accountLanguage, accountEmail, accountPassword, account2Way, lockDateTime]
                clear()
                accountLogin("createUserPath")
            elif accountInput.lower() in ["n", "no"]:
                clear()
                accountLogin("createAccount_1")
            else:
                print("\nPlease type yes or no.")
                accountLogin("createAccount_7")
        return
## Create Account Path
    elif accountAction == "createUserPath":
        if deactivateFileOpening == False:
            if currentAccountUsername != "": print("\n\nCreating Account...")
            try: pickle.load(open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Available Account.p"), "rb"))
            except OSError:
                try:
                    os.mkdir(str(os.getenv('APPDATA') + "\\Oszust Industries"))
                    pickle.dump([], open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Available Account.p"), "wb"))
                    pickle.dump("D/~RQuY(1c?BS)Iau*W7", open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Data.p"), "wb"))
                    os.mkdir(str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts"))
                except OSError:
                    shutil.rmtree(str(os.getenv('APPDATA') + "\\Oszust Industries"))
                    accountLogin("createUserPath")
            if currentAccountUsername != "":
                try:
                    currentAccountInfoPath = str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername)
                    os.mkdir(currentAccountInfoPath)
                except OSError: pass
                try:
                    currentAccountPath = str(currentAccountInfoPath + "\\" + systemName)
                    os.mkdir(currentAccountPath)
                except OSError: pass
                if currentAccountUsername.lower() == "default": packedAccountInformation = ["Default", "english", "Default", "none", "none", lockDateTime]
                pickle.dump(packedAccountInformation, open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
                clear()
        if currentAccountUsername != "": accountLogin("readSettings")
## Delete Account
    elif accountAction == "deleteAccount":
        if currentAccountUsername == "":
            print("Delete Account:\n")
            for i in availableAccounts:
                if i != "Default": print(str(availableAccounts.index(i) + 1) + ". " + i)
            accountInput = input("\nType the account number to delete the account. ").replace(" ", "")
            if accountInput == "": accountInput = "0"
            if (accountInput < str(len(tempAvailableAccounts) + 1) and int(accountInput) > 0) or accountInput in availableAccounts:
                if accountInput.isnumeric(): currentAccountUsername = availableAccounts[int(accountInput) - 1]
                else: currentAccountUsername = accountInput
                currentAccountPath = str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername + "\\" + systemName)
                accountLogin("deleteAccount")
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True: settingsMenu("", False)
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False: gameSetup()
            else:
                clear()
                print("You typed an unavailable account number.\n\n\n")
                accountLogin("deleteAccount")
        else:
            accountLogin("readSettings")
            accountInput = input("Delete Account:\n\nAre you sure you would like to permanently delete " + currentAccountUsername + "'s account from all your games? (yes/no) ").replace(" ", "")
            if accountInput.lower() in ["y", "yes"]: accountLogin("deleteAccountForever")
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True: settingsMenu("", False)
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False: gameSetup()
            elif accountInput.lower() in ["n", "no"] and accountReady == True: settingsMenu("", False)
            elif accountInput.lower() in ["n", "no"] and accountReady == False: gameSetup()
            else: accountLogin("deleteAccount")
## Delete Account Forever
    elif accountAction == "deleteAccountForever":
        print("Deleting Account...")
        shutil.rmtree(str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername))
        if currentAccountUsername.lower() != "default": availableAccounts.remove(currentAccountUsername)
        pickle.dump(availableAccounts, open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Available Account.p"), "wb"))
        clear()
        print(currentAccountUsername + "'s account has been deleted.\n\n\n")
        currentAccountUsername = ""
        gameSetup()
        return
## Rename Account
    elif accountAction == "renameAccount":
        newAccountUsername = input(str("\nRename Account:\n\nWhat would you like to rename " + currentAccountUsername + "'s account to? "))
        if accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True: settingsMenu("", False)
        elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False: gameSetup()
        elif newAccountUsername not in availableAccounts:
            if newAccountUsername.lower() not in badUsernames:
                availableAccounts.remove(currentAccountUsername)
                availableAccounts.append(newAccountUsername)
                pickle.dump(availableAccounts, open(str(os.getenv('APPDATA') + "\\Oszust Industries\\Available Account.p"), "wb"))
                currentAccountUsername = newAccountUsername
                packedAccountInformation = [currentAccountUsername, accountLanguage, accountEmail, accountPassword, account2Way, lockDateTime]
                pickle.dump(packedAccountInformation, open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
                try: accountOwnedDLC = pickle.load(open(currentAccountPath + "\\accountOwnedDLC.p", "rb"))
                except OSError: pickle.dump([currentAccountUsername], open(currentAccountPath + "\\accountOwnedDLC.p", "wb"))
                accountOwnedDLC[0] = currentAccountUsername
                pickle.dump(accountOwnedDLC, open(currentAccountPath + "\\accountOwnedDLC.p", "wb"))
                os.rename(currentAccountInfoPath, str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername))
                gameSetup()
            else:
                print("This username is unavailable.\n\n\n")
                accountLogin("renameAccount")
        else:
            print("This username is already in use.\n\n\n")
            accountLogin("renameAccount")
## Change Password
    elif accountAction == "changeAccountPassword":
        if emailconfirmed == False:
            clear()
            print("Change Account Password:")
        if accountPassword == "none":
            print("\n\n1.Add password")
            accountInput = input(str("\nType the number of the action for " + currentAccountUsername + "'s password: ")).replace(" ", "")
            if accountInput == "1":
                accountPassword = input(str("\nWhat password would you like for your account? "))
                pickle.dump([currentAccountUsername, accountLanguage, accountEmail, accountPassword, account2Way, lockDateTime], open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
                print("\n\nThe password has been added to your account.")
                gameSetup()
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True: settingsMenu("", False)
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False: gameSetup()
            else:
                clear()
                print("Please type one of the following actions.\n\n\n")
                accountLogin("changeAccountPassword")
        else:
            if emailconfirmed == False:
                accountInput = input(str("\nType your email to confirm your identity: ")).replace(" ", "")
                if accountInput == accountEmail:
                    emailCode = randrange(100000, 999999)
                    accountLogin("emailAccount_resetPasswordCode")
                    accountInput = input(str("\nA code has been sent to your email to manage your password. Type the code here: ")).replace(" ", "")
                elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True:
                    settingsMenu("", False)
                    return
                elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False:
                    gameSetup()
                    return
                else:
                    clear()
                    print("\n\nEmail doesn't match " + currentAccountUsername + "'s email.\n\n\n")
                    accountLogin("setup")
            if emailconfirmed == True or (accountInput == str(emailCode) and datetime.now() < emailExpireTime):
                emailconfirmed = True
                print("\n\n1.Change password\n2.Remove password")
                accountInput = input(str("\nType the number of the action for " + currentAccountUsername + "'s password: ")).replace(" ", "")
                if accountInput == "1":
                    accountPassword = input(str("\nWhat new password would you like for your account? "))
                    if len(accountPassword) < 5:
                        print("Your password needs to be at least five characters long.")
                        accountLogin("changeAccountPassword")
                    elif accountPassword.lower() in weakPasswords:
                        print("Your password is too weak. Create a more unique password.")
                        accountLogin("changeAccountPassword")
                    else:
                        pickle.dump([currentAccountUsername, accountLanguage, accountEmail, accountPassword, account2Way, lockDateTime], open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
                        print("\n\nThe password has been changed on your account.")
                        clear()
                        accountLogin("setup")
                elif accountInput == "2":
                    pickle.dump([currentAccountUsername, accountLanguage, accountEmail, "none", account2Way, lockDateTime], open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
                    print("\n\nThe password has been removed from your account.")
                    clear()
                    gameSetup("setup")
                elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True: settingsMenu("", False)
                elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False: gameSetup()
                else:
                    clear()
                    print("Please type one of the following actions.\n\n\n")
                    accountLogin("changeAccountPassword")
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == True: settingsMenu("", False)
            elif accountInput.lower() in ["cancel", "quit", "exit", "back", "return"] and accountReady == False: gameSetup()
            elif (accountInput == str(emailCode) and datetime.now() >= emailExpireTime) or int(accountInput) in expiredCodes:
                print("\n\nThis code has expired. A new code has been sent to your email.")
                expiredCodes = expiredCodes.append(account2Way)
                emailCode = randrange(100000, 999999)
                accountLogin("changeAccountPassword")
            else:
                clear()
                print("\n\nIncorrect verification code.\n\n\n")
                accountLogin("setup")
## Corrupt Account
    elif accountAction == "corruptAccount":
        clear()
        accountInput = input(str("Corrupt Account:\n\n\n" + currentAccountUsername + "'s account is unreadable.\n\nWould you like to delete " + currentAccountUsername + "'s account? (yes/no) ")).replace(" ", "")
        if accountInput.lower() in ["y", "yes"]: accountLogin("deleteAccountForever")
        elif accountInput.lower() in ["n", "no"]: gameSetup()
        else:
            clear()
            accountLogin("corruptAccount")
## Find Account Games
    elif accountAction == "accountGames":
        if deactivateFileOpening == False:
            try: packedAccountGames = pickle.load(open(currentAccountInfoPath + "\\accountGames.p", "rb"))
            except OSError: packedAccountGames = []
            if systemName not in packedAccountGames:
                try:
                    currentAccountPath = str(currentAccountInfoPath + "\\" + systemName)
                    os.mkdir(currentAccountPath)
                except OSError: pass
                packedAccountGames.append(systemName)
            pickle.dump(packedAccountGames, open(currentAccountInfoPath + "\\accountGames.p", "wb"))
## Read Game Settings
    elif accountAction == "readSettings":
        print("\n\nLoading Account...")
        if deactivateFileOpening == False:
            currentAccountInfoPath = str(os.getenv('APPDATA') + "\\Oszust Industries\\Accounts\\" + currentAccountUsername)
            currentAccountPath = (currentAccountInfoPath + "\\" + systemName)
        else:
            currentAccountInfoPath = ""
            currentAccountPath = ""
        accountLogin("accountGames")
        if deactivateFileOpening == False:
            try: packedAccountInformation = pickle.load(open(currentAccountInfoPath + "\\accountInformation.p", "rb"))
            except OSError: packedAccountInformation = ["N/A"]
            if resetSettings == True: packedSettings = [True, False, True, True, False]
            else:
                try: packedSettings = pickle.load(open(currentAccountPath + "\\settingsSave.p", "rb"))
                except OSError: packedSettings = [True, False, True, True, False]
        else:
            packedAccountInformation = ["N/A"]
            packedSettings = [True, False, True, True, False]
        if "N/A" not in packedAccountInformation:
            currentAccountUsername = packedAccountInformation[0]
            accountLanguage = packedAccountInformation[1]
            accountEmail = packedAccountInformation[2]
            accountPassword = packedAccountInformation[3]
            account2Way = packedAccountInformation[4]
            lockDateTime = packedAccountInformation[5]
        elif deactivateFileOpening == False:
            accountLogin("corruptAccount")
            return
        elif deactivateFileOpening == True:
            accountPassword = "none"
            account2Way = "none"
        if lockDateTime != "" and datetime.now() < lockDateTime:
            clear()
            timeLeftInLock = int(math.ceil((lockDateTime - datetime.now()).seconds / 60))
            if timeLeftInLock <= 1: print("This account is still locked for " + str(timeLeftInLock) + " more minute.\n\n\n")
            else: print("This account is still locked for " + str(timeLeftInLock) + " more minutes.\n\n\n")
            accountLogin("setup")
            return
        if accountPassword == "none" and account2Way == "none": clear()
        elif passwordAttemptsLeft <= 0:
            clear()
            print("\n\nIncorrect password.\nThe account has been locked for 5 minute.\n\n\n")
            lockDateTime = datetime.now() + timedelta(minutes=5)
            pickle.dump([currentAccountUsername, accountLanguage, accountEmail, accountPassword, account2Way, lockDateTime], open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
            accountLogin("setup")
            return
        elif accountPassword != "none":
            accountInput = input(str("\n\n\nType 'forgot password' if you have forgotten your password.\n\nThis account has a password. What is your account password? "))
            if accountInput.lower() == "forgot password":
                accountLogin("changeAccountPassword")
                return
            elif accountInput == accountPassword: clear()
            elif accountInput.lower() in ["back", "quit", "return", "logout"]:
                gameSetup()
                return
            else:
                clear()
                print("\n\nIncorrect password.\n\n\n")
                passwordAttemptsLeft -= 1
                accountLogin("readSettings")
        if deactivateFileOpening == False and account2Way != "none":
            import socket
            try:
                sock = socket.create_connection(("www.google.com", 80))
                if sock is not None:
                    sock.close
                    pass
            except OSError: account2Way = "unavailable"
        if account2Way not in ["none", "unavailable"]:
            account2Way = randrange(100000, 999999)
            accountLogin("emailAccount_verificationCode")
            accountInput = input(str("\nThis account has 2 factor verification enabled. An email has been sent with the code. Type the code here: ")).replace(" ", "")
            if accountInput == str(account2Way) and datetime.now() < emailExpireTime: clear()
            elif accountInput.lower() in ["back", "quit", "return", "logout"]:
                gameSetup()
                return
            elif (accountInput == str(account2Way) and datetime.now() >= emailExpireTime) or int(accountInput) in expiredCodes:
                clear()
                print("\n\nThis code has expired. A new code has been sent to your email.")
                expiredCodes.append(account2Way)
                accountLogin("readSettings")
            else:
                clear()
                print("\n\nIncorrect verification code.\nThe account has been locked for 1 minute.\n\n\n")
                pickle.dump([currentAccountUsername, accountLanguage, accountEmail, accountPassword, account2Way, (datetime.now() + timedelta(minutes=1))], open(currentAccountInfoPath + "\\accountInformation.p", "wb"))
                accountLogin("setup")
        elif account2Way == "unavailable":
            clear()
            print("This account has 2 factor verification enabled. We are unable to securely send a code. Please try again in a little bit.\n\n\n")
            accountLogin("setup")
        if len(packedSettings) >= 1: win10ToastActive = packedSettings[0]
        else: win10ToastActive = True
        if len(packedSettings) >= 2: resetAchievements = packedSettings[1]
        else: resetAchievements = False
        if len(packedSettings) >= 3: gameHintsActivated = packedSettings[2]
        else: gameHintsActivated = True
        if len(packedSettings) >= 4: smartWordDetector = packedSettings[3]
        else: smartWordDetector = True
        if len(packedSettings) >= 5: punishmentMode = packedSettings[4]
        else: punishmentMode = False
        accountLogin("saveSettings")
        accountLogin("readOwnedDLC")
## Save Settings
    elif accountAction == "saveSettings":
        if deactivateFileOpening == False: pickle.dump([win10ToastActive, resetAchievements, gameHintsActivated, smartWordDetector, punishmentMode], open(currentAccountPath + "\\settingsSave.p", "wb"))
## Read Owned DLC
    elif accountAction == "readOwnedDLC":
        freeGameDLC = ["Animals", "Movies", "US Cities", "Foods", "Hockey Teams", "Big Ten Colleges", "Baseball Teams", "Basketball Teams"]
        newDLCList = []
        accountActiveOwnedDLC = []
        if deactivateFileOpening == False:
            try: availablePossibleAnswers = pickle.load(open(currentAccountPath + "\\availablePossibleAnswers.p", "rb"))
            except OSError: availablePossibleAnswers = []
        else: availablePossibleAnswers = []
        if deactivateFileOpening == False:
            try: accountOwnedDLC = pickle.load(open(currentAccountPath + "\\accountOwnedDLC.p", "rb"))
            except OSError:
                pickle.dump([currentAccountUsername], open(currentAccountPath + "\\accountOwnedDLC.p", "wb"))
                accountLogin("readOwnedDLC")
                return
            if accountOwnedDLC[0] != currentAccountUsername:
                accountLogin("corruptAccount")
                return
        else: accountOwnedDLC = []
        for i in freeGameDLC:
            if i not in accountOwnedDLC:
                accountOwnedDLC.extend((i, "enable"))
                newDLCList.append(i)
        for i in accountOwnedDLC:
            if accountOwnedDLC.index(i) < (len(accountOwnedDLC) - 1) and accountOwnedDLC[accountOwnedDLC.index(i) + 1] == "enable":
                accountActiveOwnedDLC.append(i)
        if deactivateFileOpening == False: pickle.dump(accountOwnedDLC, open(currentAccountPath + "\\accountOwnedDLC.p", "wb"))
        if newDLCList != []:
            if "Animals" in newDLCList: availablePossibleAnswers.extend(("Dog", "Horse", "Cow", "Giraffe", "Tiger", "Sheep", "Zebra", "Rabbit", "Shark", "Reindeer"))
            if "Movies" in newDLCList: availablePossibleAnswers.extend(("Star Wars", "Indiana Jones", "Snow White", "Wizard of Oz", "Back to the Future", "Forrest Gump", "Jaws", "Toy Story", "Jurassic Park", "Ghostbusters"))
            if "US Cities" in newDLCList: availablePossibleAnswers.extend(("Chicago", "Detroit", "New York", "Pittsburgh", "Denver", "Houston", "New Orleans", "San Francisco", "Miami", "Boston"))
            if "Foods" in newDLCList: availablePossibleAnswers.extend(("Apple", "Popcorn", "Bacon and eggs", "Ice cream", "Cherries", "Cake", "Banana", "Pizza", "Pumpkin Pie", "Hot dogs"))
            if "Hockey Teams" in newDLCList: availablePossibleAnswers.extend(("Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche", "Blue Jackets", "Stars", "Red Wings", "Oilers", "Panthers", "Kings", "Wild", "Canadiens", "Predators", "Devils", "Islanders", "Rangers", "Senators", "Flyers", "Penguins", "Sharks", "Blues", "Lightning", "Maple Leafs", "Canucks", "Golden Knights", "Capitals", "Jets", "Kraken"))
            if "Big Ten Colleges" in newDLCList: availablePossibleAnswers.extend(("University of Wisconsin", "Purdue University", "Northwestern University", "University of Nebraska", "University of Minnesota", "University of Iowa", "University of Illinois", "Rutgers University", "Pennsylvania State University", "Ohio State University", "Michigan State University", "University of Michigan", "University of Maryland", "Indiana University"))
            if "Baseball Teams" in newDLCList: availablePossibleAnswers.extend(("Diamondbacks", "Braves", "Orioles", "Red Sox", "White Sox", "Cubs", "Reds", "Indians", "Rockies", "Tigers", "Astros", "Royals", "Angels", "Dodgers", "Marlins", "Brewers", "Twins", "Yankees", "Mets", "Athletics", "Phillies", "Pirates", "Padres", "Giants", "Mariners", "Cardinals", "Rays", "Rangers", "Blue Jays", "Nationals"))
            if "Basketball Teams" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Hawks", "Celtics", "Nets", "Hornets", "Bulls", "Cavaliers", "Mavericks", "Nuggets", "Pistons", "Warriors", "Rockets", "Pacers", "Clippers", "Lakers", "Grizzlies", "Heat", "Bucks", "Timberwolves", "Pelicans", "Knicks", "Thunder", "Magic", "76ers", "Suns", "Blazers", "Kings", "Spurs", "Raptors", "Jazz", "Wizards"))
            if deactivateFileOpening == False: pickle.dump(availablePossibleAnswers, open(currentAccountPath + "\\availablePossibleAnswers.p", "wb"))
        elif availablePossibleAnswers == []:
            if "Animals" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Dog", "Horse", "Cow", "Giraffe", "Tiger", "Sheep", "Zebra", "Rabbit", "Shark", "Reindeer"))
            if "Movies" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Star Wars", "Indiana Jones", "Snow White", "Wizard of Oz", "Back to the Future", "Forrest Gump", "Jaws", "Toy Story", "Jurassic Park", "Ghostbusters"))
            if "US Cities" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Chicago", "Detroit", "New York", "Pittsburgh", "Denver", "Houston", "New Orleans", "San Francisco", "Miami", "Boston"))
            if "Foods" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Apple", "Popcorn", "Bacon and eggs", "Ice cream", "Cherries", "Cake", "Banana", "Pizza", "Pumpkin Pie", "Hot dogs"))
            if "Hockey Teams" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche", "Blue Jackets", "Stars", "Red Wings", "Oilers", "Panthers", "Kings", "Wild", "Canadiens", "Predators", "Devils", "Islanders", "Rangers", "Senators", "Flyers", "Penguins", "Sharks", "Blues", "Lightning", "Maple Leafs", "Canucks", "Golden Knights", "Capitals", "Jets", "Kraken"))
            if "Big Ten Colleges" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("University of Wisconsin", "Purdue University", "Northwestern University", "University of Nebraska", "University of Minnesota", "University of Iowa", "University of Illinois", "Rutgers University", "Pennsylvania State University", "Ohio State University", "Michigan State University", "University of Michigan", "University of Maryland", "Indiana University"))
            if "Baseball Teams" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Diamondbacks", "Braves", "Orioles", "Red Sox", "White Sox", "Cubs", "Reds", "Indians", "Rockies", "Tigers", "Astros", "Royals", "Angels", "Dodgers", "Marlins", "Brewers", "Twins", "Yankees", "Mets", "Athletics", "Phillies", "Pirates", "Padres", "Giants", "Mariners", "Cardinals", "Rays", "Rangers", "Blue Jays", "Nationals"))
            if "Basketball Teams" in accountActiveOwnedDLC: availablePossibleAnswers.extend(("Hawks", "Celtics", "Nets", "Hornets", "Bulls", "Cavaliers", "Mavericks", "Nuggets", "Pistons", "Warriors", "Rockets", "Pacers", "Clippers", "Lakers", "Grizzlies", "Heat", "Bucks", "Timberwolves", "Pelicans", "Knicks", "Thunder", "Magic", "76ers", "Suns", "Blazers", "Kings", "Spurs", "Raptors", "Jazz", "Wizards"))
            if deactivateFileOpening == False: pickle.dump(availablePossibleAnswers, open(currentAccountPath + "\\availablePossibleAnswers.p", "wb"))

def clear():
## Clear Output
    print("\n" * 70)

def waitingAchievements():
## Threading - Waiting Achievements
    global waitingAchievementsList
    while True:
        if len(waitingAchievementsList) > 0 and toaster.notification_active() == False:
            Achievements(waitingAchievementsList[0])
            waitingAchievementsList.remove(str(waitingAchievementsList[0]))
        elif exitSystem == True and len(waitingAchievementsList) == 0: return
        else: time.sleep(0.3)

def Achievements(achievementToGain):
## Achievement System
    from pathlib import Path
    from shutil import copy
    global achievementIconLocation, achievementProgressTracker, achievementVersion, availableAchievements, currentPlaytime, earnedBronze, earnedGold, earnedPlatinum, earnedSilver, gained_Achievements, lastPlaytimeDatePlayed, playtimeStartTime, resetAchievements, toaster, waitingAchievementsList, win10ToastActive
    availableAchievements = 25
    defaultAchievementProgressTracker = [0, 10, 0, 10, 0, 10, 0, 10, 0, 32, 0, 5, 0, 5, 0, 14, 0, 30, 0, 30]
    if deactivateFileOpening == False: copy(str(Path(__file__).resolve().parent) + "\\Achievements.json", currentAccountPath)
## Last Play Date
    if exitSystem == True: lastPlaytimeDatePlayed = date.today().strftime("%m/%d/%y")
    else: lastPlaytimeDatePlayed = "Currently In-game"
## Reset Achievements
    if achievementToGain == "reset":
        if resetSettings == True: print("Loading 1/2: (Resetting settings)...\nLoading 2/2: (Resetting achievements - " + newestAchievementVersion + ")...\n\n\n")
        else: print("Loading 1/1: (Resetting achievements - " + newestAchievementVersion + ")...\n\n\n")
        achievementProgressTracker = defaultAchievementProgressTracker
        if newestAchievementVersion not in ["v1.0.0", "v1.1.0", "v1.2.0"]: gained_Achievements = [newestAchievementVersion, lastPlaytimeDatePlayed, currentPlaytime, availableAchievements, 0, 0, 0, 0,]
        elif newestAchievementVersion not in ["v1.0.0"]: gained_Achievements = [availableAchievements, 0, 0, 0, 0,]
        else: gained_Achievements = []
        ##print(gained_Achievements)
        if deactivateFileOpening == False:
            pickle.dump(achievementProgressTracker, open(currentAccountPath + "\\achievementProgressTracker.p", "wb"))
            pickle.dump(gained_Achievements, open(currentAccountPath + "\\achievementSave.p", "wb"))
            pickle.dump([], open(currentAccountPath + "\\usedWordList.p", "wb"))
        resetAchievements = False
        accountLogin("saveSettings")
        return
## Setup System
    elif achievementToGain == "setup":
        if enableAchievementThreading == True:
            import threading
            backroundAchievementThread = threading.Thread(name='waitingAchievements', target=waitingAchievements)
            waitingAchievementsList = []
            backroundAchievementThread.start()
        if deactivateFileOpening == False:
            try:
                gained_Achievements = pickle.load(open(currentAccountPath + "\\achievementSave.p", "rb"))
                if len(gained_Achievements) > 0: currentPlaytime = gained_Achievements[2]
                else: currentPlaytime = "0"
            except OSError:
                resetAchievements = True
                currentPlaytime = "0"
        else: currentPlaytime = "0"
## Remove User Achievements
        if deactivateFileOpening == False and (overrideResetAchivements == True or resetAchievements == True): Achievements("reset")
        elif deactivateFileOpening == True: Achievements("reset")
## Load Achievement System
        if deactivateFileOpening == False:
            try:
                from win10toast import ToastNotifier
                win10ToastActive = True
            except:
                try:
                    print("Installing required packages...\n\n\n")
                    os.system("pip install win10toast")
                    from win10toast import ToastNotifier
                    win10ToastActive = True
                    clear()
                except:
                    clear()
                    print("Packages failed to install.\n\nDisabling achievement notifications...\n\n\n")
                    win10ToastActive = False
            if win10ToastActive == True: toaster = ToastNotifier()
            try: achievementIconLocation = str(Path(__file__).resolve().parent)
            except: win10ToastActive = False
            try: gained_Achievements = pickle.load(open(currentAccountPath + "\\achievementSave.p", "rb"))
            except OSError: Achievements("reset")
        else: win10ToastActive = False
## Load Achievement Progress System
        if deactivateFileOpening == False and (overrideResetAchivements == False and resetAchievements == False):
            try: achievementProgressTracker = pickle.load(open(currentAccountPath + "\\achievementProgressTracker.p", "rb"))
            except OSError: achievementProgressTracker = defaultAchievementProgressTracker
        else: achievementProgressTracker = defaultAchievementProgressTracker
## Compatibility Versions
        if deactivateFileOpening == False:
            pickle.dump(achievementProgressTracker, open(currentAccountPath + "\\achievementProgressTracker.p", "wb"))
            if len(gained_Achievements) > 0:
                achievementVersion = gained_Achievements[0]
                if ("v1" not in str(achievementVersion)) and (len(gained_Achievements) >= 7) and ("Achievement" not in str(gained_Achievements[6])): achievementVersion = "v1.2.0"
                elif str(achievementVersion) == "0" or str(achievementVersion) == str(availableAchievements): achievementVersion = "v1.1.0"
                elif "v1" not in str(achievementVersion): achievementVersion = "v1.0.0"
            else: achievementVersion = "v1.0.0"
            if achievementVersion not in ["v1.0.0", "v1.1.0", "v1.2.0"]:
                playtimeStartTime = datetime.now()
                currentPlaytime = float(gained_Achievements[2])
                earnedBronze = int(gained_Achievements[4])
                earnedSilver = int(gained_Achievements[5])
                earnedGold = int(gained_Achievements[6])
                earnedPlatinum = int(gained_Achievements[7])
            elif achievementVersion not in ["v1.0.0"]:
                earnedBronze = int(gained_Achievements[1])
                earnedSilver = int(gained_Achievements[2])
                earnedGold = int(gained_Achievements[3])
                earnedPlatinum = int(gained_Achievements[4])
        Achievements("saving")
## System Achievements
    if deactivateFileOpening == False and win10ToastActive == True and toaster.notification_active() and enableAchievementThreading == True:
        waitingAchievementsList.append(str(achievementToGain))
        return
    if deactivateFileOpening == False and achievementToGain not in ["reset", "setup", "ready"] and "Progress" not in achievementToGain and achievementToGain not in gained_Achievements:
        if achievementToGain == "Achievement_Welcome":
            if win10ToastActive == True: toaster.show_toast("Bronze - Welcome to the Game", str("Start Hangman for the first time." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Welcome.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Keep_Playing":
            if win10ToastActive == True: toaster.show_toast("Bronze - Thirsty for More?", str("Start a second game." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Keep_Playing.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Stop_Playing":
            if win10ToastActive == True: toaster.show_toast("Bronze - Done so Soon?", str("Stop playing Hangman." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Stop_Playing.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Solve_Wrong":
            if win10ToastActive == True: toaster.show_toast("Bronze - Swing and a Miss", str("Wrongly solve an entire word." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Solve_Wrong.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Winner":
            if win10ToastActive == True: toaster.show_toast("Bronze - We are the Champions", str("Win a game of Hangman." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Winner.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Same_Letter":
            if win10ToastActive == True: toaster.show_toast("Bronze - Hello? Hello? Anybody home?", str("Try the same letter more than once." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Same_Letter.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Alphabet":
            if win10ToastActive == True: toaster.show_toast("Bronze - 00110001", str("Type a character that isn't from the alphabet." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Alphabet.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Bronze"
        elif achievementToGain == "Achievement_Solve_Correct":
            if win10ToastActive == True: toaster.show_toast("Silver - Walking Dictionary", str("Correctly solve an entire word." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Solve_Correct.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Silver"
        elif achievementToGain == "Achievement_Terminate":
            if win10ToastActive == True: toaster.show_toast("Silver - Hasta La Vista, Baby", str("Terminate a game while playing." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Terminate.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Silver"
        elif achievementToGain == "Achievement_Close_Call":
            if win10ToastActive == True: toaster.show_toast("Silver - Winning's Winning", str("Win a game with only one life left." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Close_Call.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Silver"
        elif achievementToGain == "Achievement_Hot_Streak":
            if win10ToastActive == True: toaster.show_toast("Silver - You're on Fire!", str("Go on a streak of 5 correct games." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Hot_Streak.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Silver"
        elif achievementToGain == "Achievement_Cold_Streak":
            if win10ToastActive == True: toaster.show_toast("Silver - Geez, Pick up a Book", str("Go on a streak of 5 wrong games." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Cold_Streak.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Silver"
        elif achievementToGain == "Achievement_All_Topics":
            if win10ToastActive == True: toaster.show_toast("Silver - 100% Completion", str("Play all of the game's words." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Topics.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Silver"
        elif achievementToGain == "Achievement_Solve_Correct_No_Help":
            if win10ToastActive == True: toaster.show_toast("Gold - How did you Know?", str("Correctly solve an entire word without using any letter guesses." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Solve_Correct_No_Help.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_Hard_Mode":
            if win10ToastActive == True: toaster.show_toast("Gold - Challenge Accepted", str("Win a game of Hangman without hints activated." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_Hard_Mode.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Animals":
            if win10ToastActive == True: toaster.show_toast("Gold - Zoologist", str("Complete all the game words in the animals category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Animals.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Movies":
            if win10ToastActive == True: toaster.show_toast("Gold - Cinephile", str("Complete all the game words in the movies category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Movies.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Cities":
            if win10ToastActive == True: toaster.show_toast("Gold - Architect", str("Complete all the game words in the US cities category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Cities.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Foods":
            if win10ToastActive == True: toaster.show_toast("Gold - Gastronome", str("Complete all the game words in the foods category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Foods.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Hockey":
            if win10ToastActive == True: toaster.show_toast("Gold - Mr. Hockey", str("Complete all the game words in the hockey teams category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Hockey.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Big_Ten_Colleges":
            if win10ToastActive == True: toaster.show_toast("Gold - Stagg Championship Trophy", str("Complete all the game words in the Big Ten Colleges category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Big_Ten_Colleges.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Baseball":
            if win10ToastActive == True: toaster.show_toast("Gold - Play Ball", str("Complete all the game words in the baseball teams category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Baseball.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Basketball":
            if win10ToastActive == True: toaster.show_toast("Gold - Swish", str("Complete all the game words in the basketball teams category." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Basketball.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Gold"
        elif achievementToGain == "Achievement_All_Correct":
            if win10ToastActive == True: toaster.show_toast("Gold - A+ Score", str("Get every question in Hangman correct." + "\n(" + currentAccountUsername + ")"), icon_path = achievementIconLocation + "\Achievement Icons\Achievement_All_Correct.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Platinum"
        elif achievementToGain == "Achievement_100%_Achievement":
            if win10ToastActive == True: toaster.show_toast("Platinum - Hangman Master", str("Get all " + str(availableAchievements) + " achievements in Hangman." + "\n(" + currentAccountUsername + ")"), icon_path = str(Path(__file__).resolve().parent) + "\Achievement Icons\Achievement_100%_Achievement.ico", duration=5, threaded=enableAchievementThreading)
            if achievementVersion not in ["v1.0.0"]: medalEarned = "Platinum"
        elif achievementToGain != "saving": print("GAME ERROR(No Achievement with that name found)")
        if achievementVersion not in ["v1.0.0"] and achievementToGain != "saving":
            if medalEarned == "Bronze": earnedBronze += 1
            elif medalEarned == "Silver": earnedSilver += 1
            elif medalEarned == "Gold": earnedGold += 1
            elif medalEarned == "Platinum": earnedPlatinum += 1
        if achievementVersion not in ["v1.0.0", "v1.1.0", "v1.2.0"]:
            duration = datetime.now() - playtimeStartTime
            currentPlaytime = round(float(currentPlaytime) + duration.total_seconds(), 2)
            playtimeStartTime = datetime.now()
        if achievementVersion not in ["v1.0.0", "v1.1.0", "v1.2.0"]: gained_Achievements = [str(achievementVersion)] + [str(lastPlaytimeDatePlayed)] + [str(currentPlaytime)] + [str(availableAchievements)] + [str(earnedBronze)] + [str(earnedSilver)] + [str(earnedGold)] + [str(earnedPlatinum)] + gained_Achievements[8:]
        elif achievementVersion not in ["v1.0.0"]: gained_Achievements = [str(availableAchievements)] + [str(earnedBronze)] + [str(earnedSilver)] + [str(earnedGold)] + [str(earnedPlatinum)] + gained_Achievements[5:]
        else: gained_Achievements = gained_Achievements
        if achievementToGain != "saving": gained_Achievements.append(achievementToGain)
        if achievementVersion not in ["v1.0.0", "v1.1.0"] and achievementToGain != "saving": gained_Achievements.append(str(date.today().strftime("%m/%d/%y") + " " + datetime.now().strftime("%I:%M %p")))
        if overrideResetAchivements == False and resetAchievements == False and deactivateFileOpening == False: pickle.dump(gained_Achievements, open(currentAccountPath + "\\achievementSave.p", "wb"))
        if "Achievement_100%_Achievement" not in gained_Achievements and ((int(earnedBronze) + int(earnedSilver) + int(earnedGold) + int(earnedPlatinum)) >= (availableAchievements - 1)): Achievements("Achievement_100%_Achievement")
## System Achievements Progress
    elif deactivateFileOpening == False and achievementToGain not in ["reset", "setup", "ready"] and "Progress" in achievementToGain:
        achievementToGain = achievementToGain.replace("Achievement_Progress_", "")
        if len(achievementProgressTracker) >= 1: animalsCategory = int(achievementProgressTracker[0])
        else: animalsCategory = int(defaultAchievementProgressTracker[0])
        if len(achievementProgressTracker) >= 2: maxAnimalsCategory = int(achievementProgressTracker[1])
        else: maxAnimalsCategory = int(defaultAchievementProgressTracker[1])
        if len(achievementProgressTracker) >= 3: moviesCategory = int(achievementProgressTracker[2])
        else: moviesCategory = int(defaultAchievementProgressTracker[2])
        if len(achievementProgressTracker) >= 4: maxMoviesCategory = int(achievementProgressTracker[3])
        else: maxMoviesCategory = int(defaultAchievementProgressTracker[3])
        if len(achievementProgressTracker) >= 5: USCitiesCategory = int(achievementProgressTracker[4])
        else: USCitiesCategory = int(defaultAchievementProgressTracker[4])
        if len(achievementProgressTracker) >= 6: maxUSCitiesCategory = int(achievementProgressTracker[5])
        else: maxUSCitiesCategory = int(defaultAchievementProgressTracker[5])
        if len(achievementProgressTracker) >= 7: foodsCategory = int(achievementProgressTracker[6])
        else: foodsCategory = int(defaultAchievementProgressTracker[6])
        if len(achievementProgressTracker) >= 8: maxFoodsCategory = int(achievementProgressTracker[7])
        else: maxFoodsCategory = int(defaultAchievementProgressTracker[7])
        if len(achievementProgressTracker) >= 9: HockeyTeamsCategory = int(achievementProgressTracker[8])
        else: HockeyTeamsCategory = int(defaultAchievementProgressTracker[8])
        if len(achievementProgressTracker) >= 10: maxHockeyTeamsCategory = int(achievementProgressTracker[9])
        else: maxHockeyTeamsCategory = int(defaultAchievementProgressTracker[9])
        if len(achievementProgressTracker) >= 11: winningStreak = int(achievementProgressTracker[10])
        else: winningStreak = int(defaultAchievementProgressTracker[10])
        if len(achievementProgressTracker) >= 12: maxWinningStreak = int(achievementProgressTracker[11])
        else: maxWinningStreak = int(defaultAchievementProgressTracker[11])
        if len(achievementProgressTracker) >= 13: losingStreak = int(achievementProgressTracker[12])
        else: losingStreak = int(defaultAchievementProgressTracker[12])
        if len(achievementProgressTracker) >= 14: maxLosingStreak = int(achievementProgressTracker[13])
        else: maxLosingStreak = int(defaultAchievementProgressTracker[13])
        if len(achievementProgressTracker) >= 15: BigTenCollegesCategory = int(achievementProgressTracker[14])
        else: BigTenCollegesCategory = int(defaultAchievementProgressTracker[14])
        if len(achievementProgressTracker) >= 16: maxBigTenCollegesCategoryCategory = int(achievementProgressTracker[15])
        else: maxBigTenCollegesCategoryCategory = int(defaultAchievementProgressTracker[15])
        if len(achievementProgressTracker) >= 17: BaseballTeamsCategory = int(achievementProgressTracker[16])
        else: BaseballTeamsCategory = int(defaultAchievementProgressTracker[16])
        if len(achievementProgressTracker) >= 18: maxBaseballTeamsCategory = int(achievementProgressTracker[17])
        else: maxBaseballTeamsCategory = int(defaultAchievementProgressTracker[17])
        if len(achievementProgressTracker) >= 19: BasketballTeamsCategory = int(achievementProgressTracker[18])
        else: BasketballTeamsCategory = int(defaultAchievementProgressTracker[18])
        if len(achievementProgressTracker) >= 20: maxBasketballTeamsCategory = int(achievementProgressTracker[19])
        else: maxBasketballTeamsCategory = int(defaultAchievementProgressTracker[19])
        if achievementToGain == "Animals": animalsCategory += 1
        elif achievementToGain == "Movies": moviesCategory += 1
        elif achievementToGain == "USCities": USCitiesCategory += 1
        elif achievementToGain == "Foods": foodsCategory += 1
        elif achievementToGain == "HockeyTeams": HockeyTeamsCategory += 1
        elif achievementToGain == "BigTenColleges": BigTenCollegesCategory += 1
        elif achievementToGain == "BaseballTeams": BaseballTeamsCategory += 1
        elif achievementToGain == "BasketballTeams": BasketballTeamsCategory += 1
        elif achievementToGain == "WinStreak":
            winningStreak += 1
            losingStreak = 0
        elif achievementToGain == "LoseStreak":
            losingStreak += 1
            winningStreak = 0
        elif achievementToGain == "100Check" and len(usedWordList) >= 86 and winningStreak >= 86: Achievements("Achievement_All_Correct")
        if "Achievement_All_Animals" not in gained_Achievements and ("Animals" in accountActiveOwnedDLC and animalsCategory >= maxAnimalsCategory): Achievements("Achievement_All_Animals")
        if "Achievement_All_Movies" not in gained_Achievements and ("Movies" in accountActiveOwnedDLC and moviesCategory >= maxMoviesCategory): Achievements("Achievement_All_Movies")
        if "Achievement_All_Cities" not in gained_Achievements and ("US Cities" in accountActiveOwnedDLC and USCitiesCategory >= maxUSCitiesCategory): Achievements("Achievement_All_Cities")
        if "Achievement_All_Foods" not in gained_Achievements and ("Foods" in accountActiveOwnedDLC and foodsCategory >= maxFoodsCategory): Achievements("Achievement_All_Foods")
        if "Achievement_All_Hockey" not in gained_Achievements and ("Hockey Teams" in accountActiveOwnedDLC and HockeyTeamsCategory >= maxHockeyTeamsCategory): Achievements("Achievement_All_Hockey")
        if "Achievement_All_Big_Ten_Colleges" not in gained_Achievements and ("Big Ten Colleges" in accountActiveOwnedDLC and BigTenCollegesCategory >= maxBigTenCollegesCategoryCategory): Achievements("Achievement_All_Big_Ten_Colleges")
        if "Achievement_All_Baseball" not in gained_Achievements and ("Baseball Teams" in accountActiveOwnedDLC and BaseballTeamsCategory >= maxBaseballTeamsCategory): Achievements("Achievement_All_Baseball")
        if "Achievement_All_Basketball" not in gained_Achievements and ("Basketball Teams" in accountActiveOwnedDLC and BaseballTeamsCategory >= maxBaseballTeamsCategory): Achievements("Achievement_All_Basketball")
## Streak Counter
        if "Achievement_Hot_Streak" not in gained_Achievements and (winningStreak >= maxWinningStreak): Achievements("Achievement_Hot_Streak")
        elif "Achievement_Cold_Streak" not in gained_Achievements and (losingStreak >= maxLosingStreak): Achievements("Achievement_Cold_Streak")
## Save Progress
        achievementProgressTracker = [animalsCategory, maxAnimalsCategory, moviesCategory, maxMoviesCategory, USCitiesCategory, maxUSCitiesCategory, foodsCategory, maxFoodsCategory, HockeyTeamsCategory, maxHockeyTeamsCategory, winningStreak, maxWinningStreak, losingStreak, maxLosingStreak, BigTenCollegesCategory, maxBigTenCollegesCategoryCategory, BaseballTeamsCategory, maxBaseballTeamsCategory, BasketballTeamsCategory, maxBasketballTeamsCategory]
        if overrideResetAchivements == False and resetAchievements == False and deactivateFileOpening == False: pickle.dump(achievementProgressTracker, open(currentAccountPath + "\\achievementProgressTracker.p", "wb"))

def startMenu(menuOption):
## Game Start Menu
    global allWordsUsed, availablePossibleAnswers, oneGamePlayed
    if resetSettings == True and (overrideResetAchivements == False and resetAchievements == False): print("Loading 1/1: (Resetting settings)...\n\n\n")
    if menuOption == "": print("Welcome to Hangman. " + gameVersion + "\nCreated and published by Oszust Industries\n\n\n")
    if allWordsUsed == False: print("1 - Start Game\n2 - Reset Completed Words\n3 - Game Help\n4 - DLC Management\n5 - Game Settings")
    else: print("No Game Words Left (Reset your completed words)\n2 - Reset Completed Words\n3 - Game Help\n4 - DLC Management\n5 - Game Settings")
    if (deactivateFileOpening == True or enableAccountSystem == False) and currentAccountUsername != "Guest": print("6 - Quit Game")
    else: print("6 - Logout of Account\n7 - Quit Game")
    if allWordsUsed == False:
        if (deactivateFileOpening == True or enableAccountSystem == False) and currentAccountUsername != "Guest": menuOption = input(str("\nType a number. (1/2/3/4/5/6) ")).replace(" ", "")
        else: menuOption = input(str("\nType a number. (1/2/3/4/5/6/7) ")).replace(" ", "")
    else:
        if (deactivateFileOpening == True or enableAccountSystem == False) and currentAccountUsername != "Guest": menuOption = input(str("\nType a number. (2/3/4/5/6) ")).replace(" ", "")
        else: menuOption = input(str("\nType a number. (2/3/4/5/6/7) ")).replace(" ", "")
    if menuOption.lower() in ["1", "start", "game"] and allWordsUsed == False:
        if oneGamePlayed == True: Achievements("Achievement_Keep_Playing")
        Achievements("Achievement_Welcome")
        oneGamePlayed = False
        menuOption = ""
        gameStart()
    elif menuOption.lower() in ["2", "reset"]:
        clear()
        availablePossibleAnswers = []
        for i in accountOwnedDLC:
            if accountOwnedDLC.index(i) < (len(accountOwnedDLC) - 1) and accountOwnedDLC[accountOwnedDLC.index(i) + 1] == "enable":
                if i == "Animals": availablePossibleAnswers.extend(("Dog", "Horse", "Cow", "Giraffe", "Tiger", "Sheep", "Zebra", "Rabbit", "Shark", "Reindeer"))
                elif i == "Movies": availablePossibleAnswers.extend(("Star Wars", "Indiana Jones", "Snow White", "Wizard of Oz", "Back to the Future", "Forrest Gump", "Jaws", "Toy Story", "Jurassic Park", "Ghostbusters"))
                elif i == "US Cities": availablePossibleAnswers.extend(("Chicago", "Detroit", "New York", "Pittsburgh", "Denver", "Houston", "New Orleans", "San Francisco", "Miami", "Boston"))
                elif i == "Foods": availablePossibleAnswers.extend(("Apple", "Popcorn", "Bacon and eggs", "Ice cream", "Cherries", "Cake", "Banana", "Pizza", "Pumpkin Pie", "Hot dogs"))
                elif i == "Hockey Teams": availablePossibleAnswers.extend(("Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche", "Blue Jackets", "Stars", "Red Wings", "Oilers", "Panthers", "Kings", "Wild", "Canadiens", "Predators", "Devils", "Islanders", "Rangers", "Senators", "Flyers", "Penguins", "Sharks", "Blues", "Lightning", "Maple Leafs", "Canucks", "Golden Knights", "Capitals", "Jets", "Kraken"))
                elif i == "Big Ten Colleges": availablePossibleAnswers.extend(("University of Wisconsin", "Purdue University", "Northwestern University", "University of Nebraska", "University of Minnesota", "University of Iowa", "University of Illinois", "Rutgers University", "Pennsylvania State University", "Ohio State University", "Michigan State University", "University of Michigan", "University of Maryland", "Indiana University"))
                elif i == "Baseball Teams": availablePossibleAnswers.extend(("Diamondbacks", "Braves", "Orioles", "Red Sox", "White Sox", "Cubs", "Reds", "Indians", "Rockies", "Tigers", "Astros", "Royals", "Angels", "Dodgers", "Marlins", "Brewers", "Twins", "Yankees", "Mets", "Athletics", "Phillies", "Pirates", "Padres", "Giants", "Mariners", "Cardinals", "Rays", "Rangers", "Blue Jays", "Nationals"))
                if deactivateFileOpening == False: pickle.dump(availablePossibleAnswers, open(currentAccountPath + "\\availablePossibleAnswers.p", "wb"))
        oneGamePlayed = False
        if len(availablePossibleAnswers) > 0: allWordsUsed = False
        print("All completed words reset.\n\n\n")
        startMenu("")
    elif menuOption.lower() in ["3", "help", "tips"]:
        clear()
        print("Game Help:\n")
        if gameHintsActivated == True: print("\nThe game will give you a category and a hint.")
        else: print("\nThe game will give you a category")
        print("The word you must guess is from that category.\n\nEnter 'DLC Management' on the main menu to disable categories that you don't want in your game.\n\nType a letter, and if it appears in the word, the blank spots will fill with that letter.\nIf the letter doesn't appear in the word, you will lose one of your three lives.\nOnce out of lives, you lose the game.\n\nIf you know the entire word/phrase, type 'solve'.\nYou will have one chance to guess the entire word/phrase.")
        if smartWordDetector == True: print("Smart Word Detector is active and allows you to type the entire word/phrase without having to type 'solve'.")
        if punishmentMode == True: print("\nPunishment Mode is active and will cause you to lose a life if you don't type a letter from the alphabet or type a letter you already used.")
        print("\n\n")
        startMenu("")
    elif menuOption.lower() in ["4", "dlc", "management"]:
        clear()
        DLCManagement()
    elif menuOption.lower() in ["5", "settings"]: settingsMenu("", False)
    elif menuOption.lower() in ["6", "logout", "back"] and (deactivateFileOpening == False or currentAccountUsername == "Guest") and enableAccountSystem == True: accountLogin("logout")
    elif menuOption.lower() in ["6", "quit", "exit"] and (deactivateFileOpening == True or enableAccountSystem == False):
        if oneGamePlayed == True: Achievements("Achievement_Stop_Playing")
        accountLogin("quit")
    elif menuOption.lower() in ["7", "quit", "exit"] and (deactivateFileOpening == False or currentAccountUsername == "Guest") and enableAccountSystem == True:
        if oneGamePlayed == True: Achievements("Achievement_Stop_Playing")
        accountLogin("quit")
    else:
        clear()
        if allWordsUsed == False:
            if (deactivateFileOpening == True or enableAccountSystem == False) and currentAccountUsername != "Guest": print("\n\nPlease type a number. (1/2/3/4/5/6)\n\n\n")
            else: menuOption = print("\n\nPlease type a number. (1/2/3/4/5/6/7)\n\n\n")
        else:
            if (deactivateFileOpening == True or enableAccountSystem == False) and currentAccountUsername != "Guest": print("\n\nPlease type a number. (2/3/4/5/6)\n\n\n")
            else: menuOption = print("\n\nPlease type a number. (2/3/4/5/6/7)\n\n\n")
        startMenu("error")

def DLCManagement():
## Manage Account DLC
    global allWordsUsed, DLCTopicList
    allAvailableDLC = ["Animals", "Movies", "US Cities", "Foods", "Hockey Teams", "Big Ten Colleges", "Baseball Teams", "Basketball Teams"]
    if len(availablePossibleAnswers) > 0: allWordsUsed = False
    else: allWordsUsed = True
    print("DLC Management:\n\nType 'save' to return to the menu.\n\n")
    for i in allAvailableDLC:
        if i not in accountOwnedDLC: print(str(allAvailableDLC.index(i) + 1) + ". " + i + " - Not Owned")
        elif accountOwnedDLC[accountOwnedDLC.index(i) + 1] == "enable": print(str(allAvailableDLC.index(i) + 1) + ". " + i + " - Active")
        elif accountOwnedDLC[accountOwnedDLC.index(i) + 1] == "disable": print(str(allAvailableDLC.index(i) + 1) + ". " + i + " - Inactive")
    if "Word Creator" in accountOwnedDLC: print("\n" + str(allAvailableDLC.index(i) + 2) + ". Word Creator")
    menuOption = input(str("\nType a DLC number to enable/disable it. ")).replace(" ", "")
    if menuOption.lower() in ["done", "back", "mainmenu", "menu", "save", "game", "exit"]:
        clear()
        startMenu("")
        return
    elif ("Word Creator" in accountOwnedDLC and menuOption.lower() in ["wordcreator", "creator"]) or ("Word Creator" in accountOwnedDLC and int(menuOption) == allAvailableDLC.index(i) + 2): print("GOOD")
    elif (menuOption.isnumeric() and int(menuOption) < len(allAvailableDLC) + 1 and int(menuOption) > 0) or menuOption in allAvailableDLC:
        if menuOption.isnumeric() and int(menuOption) < len(allAvailableDLC) + 1: menuOption = allAvailableDLC[int(menuOption) - 1]
        if menuOption in accountOwnedDLC: menuOption = accountOwnedDLC.index(menuOption)
        else:
            clear()
            print("You don't own this DLC.\n\n\n")
            DLCManagement()
            return
        if accountOwnedDLC[menuOption] == "Animals": DLCTopicList = ["Dog", "Horse", "Cow", "Giraffe", "Tiger", "Sheep", "Zebra", "Rabbit", "Shark", "Reindeer"]
        elif accountOwnedDLC[menuOption] == "Movies": DLCTopicList = ["Star Wars", "Indiana Jones", "Snow White", "Wizard of Oz", "Back to the Future", "Forrest Gump", "Jaws", "Toy Story", "Jurassic Park", "Ghostbusters"]
        elif accountOwnedDLC[menuOption] == "US Cities": DLCTopicList = ["Chicago", "Detroit", "New York", "Pittsburgh", "Denver", "Houston", "New Orleans", "San Francisco", "Miami", "Boston"]
        elif accountOwnedDLC[menuOption] == "Foods": DLCTopicList = ["Apple", "Popcorn", "Bacon and eggs", "Ice cream", "Cherries", "Cake", "Banana", "Pizza", "Pumpkin Pie", "Hot dogs"]
        elif accountOwnedDLC[menuOption] == "Hockey Teams": DLCTopicList = ["Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche", "Blue Jackets", "Stars", "Red Wings", "Oilers", "Panthers", "Kings", "Wild", "Canadiens", "Predators", "Devils", "Islanders", "Rangers", "Senators", "Flyers", "Penguins", "Sharks", "Blues", "Lightning", "Maple Leafs", "Canucks", "Golden Knights", "Capitals", "Jets", "Kraken"]
        elif accountOwnedDLC[menuOption] == "Big Ten Colleges": DLCTopicList = ["University of Wisconsin", "Purdue University", "Northwestern University", "University of Nebraska", "University of Minnesota", "University of Iowa", "University of Illinois", "Rutgers University", "Pennsylvania State University", "Ohio State University", "Michigan State University", "University of Michigan", "University of Maryland", "Indiana University"]
        elif accountOwnedDLC[menuOption] == "Baseball Teams": DLCTopicList = ["Diamondbacks", "Braves", "Orioles", "Red Sox", "White Sox", "Cubs", "Reds", "Indians", "Rockies", "Tigers", "Astros", "Royals", "Angels", "Dodgers", "Marlins", "Brewers", "Twins", "Yankees", "Mets", "Athletics", "Phillies", "Pirates", "Padres", "Giants", "Mariners", "Cardinals", "Rays", "Rangers", "Blue Jays", "Nationals"]
        elif accountOwnedDLC[menuOption] == "Basketball Teams": DLCTopicList = ["Hawks", "Celtics", "Nets", "Hornets", "Bulls", "Cavaliers", "Mavericks", "Nuggets", "Pistons", "Warriors", "Rockets", "Pacers", "Clippers", "Lakers", "Grizzlies", "Heat", "Bucks", "Timberwolves", "Pelicans", "Knicks", "Thunder", "Magic", "76ers", "Suns", "Blazers", "Kings", "Spurs", "Raptors", "Jazz", "Wizards"]
        if accountOwnedDLC[menuOption + 1] == "enable":
            accountOwnedDLC[menuOption + 1] = "disable"
            for i in DLCTopicList:
                if i in availablePossibleAnswers: availablePossibleAnswers.remove(i)
        elif accountOwnedDLC[menuOption + 1] == "disable":
            accountOwnedDLC[menuOption + 1] = "enable"
            for i in DLCTopicList:
                if i not in availablePossibleAnswers: availablePossibleAnswers.append(i)
        if deactivateFileOpening == False:
            pickle.dump(accountOwnedDLC, open(currentAccountPath + "\\accountOwnedDLC.p", "wb"))
            pickle.dump(availablePossibleAnswers, open(currentAccountPath + "\\availablePossibleAnswers.p", "wb"))
        clear()
        DLCManagement()
    else:
        clear()
        print("You typed an unavailable DLC number.\n\n\n")
        DLCManagement()

def settingsMenu(settingsChange, showSettingsError):
## Settings Menu
    global gameHintsActivated, gamemode, punishmentMode, resetAchievements, settingsUserChange, smartWordDetector, win10ToastActive
    if gameHintsActivated == False and smartWordDetector == False and punishmentMode == True: gamemode = "Hard"
    elif gameHintsActivated == True and smartWordDetector == True and punishmentMode == False: gamemode = "Easy"
    else: gamemode = "Medium"
    if deactivateFileOpening == True:
        win10ToastActive = False
        resetAchievements = False
    if settingsChange == "":
        clear()
        if showSettingsError == True: print("Please type one of the following options.\n\n")
        print("Settings Menu:\n\nType the number of the setting to change.\nType 'default' to set all settings to their defaults.\nType 'cancel' to return to settings and cancel the change.\nType 'save' when you're ready to get back to the game.\n\n")
        if deactivateFileOpening == False:
            if achievementVersion == newestAchievementVersion: print("Current account achievement version: " + str(achievementVersion) + " - Current")
            else: print("Current account achievement version: " + str(achievementVersion) + " - Outdated")
        else: resetAchievements = False
        print("Current game mode: " + str(gamemode) + "\n\n\nGame Settings:\n1. Achievement Notifications Activated = " + str(win10ToastActive) + "\n2. Reset & Update Achievements = " + str(resetAchievements) + "\n3. Game Hints Activated = " + str(gameHintsActivated) + "\n4. Smart Word Detector Activated = " + str(smartWordDetector) + "\n5. Punishment Mode Activated = " + str(punishmentMode))
        if deactivateFileOpening == False: print("\n\nAccount Settings:\n6. Rename Account\n7. Manage Account Password\n8. Delete Account")
        else: print("\n\nAccount settings can't be changed while deactivateFileOpening is set to True.")
        settingsChange = input(str("\nWhat setting would you like to change? ")).replace(" ", "")
        showSettingsError = False
    if settingsChange.lower() in ["done", "back", "mainmenu", "menu", "save", "game", "exit"]:
        accountLogin("saveSettings")
        clear()
        startMenu("")
    elif settingsChange.lower() in ["default", "defaults"]:
        packedSettings = [True, False, True, True, False]
        win10ToastActive = packedSettings[0]
        resetAchievements = packedSettings[1]
        gameHintsActivated = packedSettings[2]
        smartWordDetector = packedSettings[3]
        punishmentMode = packedSettings[4]
        settingsMenu("", False)
    elif settingsChange in ["1", "notifications", "achievements"]:
        print("\n\nWould you like to change Achievement Notifications to on or off? (On/Off) ")
        settingsUserChange = input(str("")).replace(" ", "")
        if settingsUserChange.lower() in ["back", "settings", "cancel"]: settingsMenu("", False)
        elif settingsUserChange.lower() in ["true", "on", "activate", "turnon", "yes", "enable"]:
            win10ToastActive = True
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["false", "off", "deactivate", "turnoff", "no", "disable"]:
            win10ToastActive = False
            settingsMenu("", False)
        else: settingsMenu("1", False)
    elif settingsChange in ["2", "reset"]:
        print("\n\nWould you like to Reset Achievements on the next game launch? (Yes/No) ")
        settingsUserChange = input(str("")).replace(" ", "")
        if settingsUserChange.lower() in ["back", "settings", "cancel"]: settingsMenu("", False)
        elif settingsUserChange.lower() in ["true", "on", "activate", "turnon", "yes", "enable"]:
            resetAchievements = True
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["false", "off", "deactivate", "turnoff", "no", "disable"]:
            resetAchievements = False
            settingsMenu("", False)
        else: settingsMenu("2", False)
    elif settingsChange in ["3", "activategamehints", "activatehints", "gamehints", "hints"]:
        print("\n\nWould you like to change Game Hints to on or off? (On/Off) ")
        settingsUserChange = input(str("")).replace(" ", "")
        if settingsUserChange.lower() in ["back", "settings", "cancel"]:
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["true", "on", "activate", "turnon", "yes", "enable"]:
            gameHintsActivated = True
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["false", "off", "deactivate", "turnoff", "no", "disable"]:
            gameHintsActivated = False
            settingsMenu("", False)
        else: settingsMenu("3", False)
    elif settingsChange in ["4", "smart", "word", "detect", "smartWordDetector"]:
        print("\n\nWould you like to change Smart Word Detector to on or off? (On/Off) ")
        settingsUserChange = input(str("")).replace(" ", "")
        if settingsUserChange.lower() in ["back", "settings", "cancel"]: settingsMenu("", False)
        elif settingsUserChange.lower() in ["true", "on", "activate", "turnon", "yes", "enable"]:
            smartWordDetector = True
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["false", "off", "deactivate", "turnoff", "no", "disable"]:
            smartWordDetector = False
            settingsMenu("", False)
        else: settingsMenu("4", False)
    elif settingsChange in ["5", "punishment", "punish"]:
        print("\n\nWould you like to change Punishment Mode to on or off? (On/Off) ")
        settingsUserChange = input(str("")).replace(" ", "")
        if settingsUserChange.lower() in ["back", "settings", "cancel"]: settingsMenu("", False)
        elif settingsUserChange.lower() in ["true", "on", "activate", "turnon", "yes", "enable"]:
            punishmentMode = True
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["false", "off", "deactivate", "turnoff", "no", "disable"]:
            punishmentMode = False
            settingsMenu("", False)
        else: settingsMenu("5", False)
    elif settingsChange in ["mode", "difficulty", "gamemode"]:
        print("\n\nWould you like to change the game mode to easy or hard? (Easy/Medium/Hard) ")
        settingsUserChange = input(str("")).replace(" ", "")
        if settingsUserChange.lower() in ["back", "settings", "cancel"]: settingsMenu("", False)
        elif settingsUserChange.lower() in ["easy"]:
            gameHintsActivated = True
            smartWordDetector = True
            punishmentMode = False
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["medium", "normal", "classic"]:
            gameHintsActivated = False
            smartWordDetector = True
            punishmentMode = False
            settingsMenu("", False)
        elif settingsUserChange.lower() in ["hard"]:
            gameHintsActivated = False
            smartWordDetector = False
            punishmentMode = True
            settingsMenu("", False)
        else: settingsMenu("mode", False)
    elif settingsChange in ["6", "rename"] and deactivateFileOpening == False: accountLogin("renameAccount")
    elif settingsChange in ["7", "password"] and deactivateFileOpening == False: accountLogin("changeAccountPassword")
    elif settingsChange in ["8", "delete"] and deactivateFileOpening == False:
        accountLogin("deleteAccount")
        return
    else: settingsMenu("", True)

def gameStart():
## Load Game
    global allWordsUsed, availablePossibleAnswers, currentCategory, firstTry, found, gameLives, lowerAnswer, menuOption, properAnswer, usedLetters
    print("\n\nLoading Game...")
    clear()
    print("-" * 60)
    firstTry = True
    found = []
    gameLives = 3
    usedLetters = []
## Find Game Answer
    if len(availablePossibleAnswers) > 0:
        properAnswer = random.choice(availablePossibleAnswers)
## Find Game Category
        if properAnswer in ["Dog", "Horse", "Cow", "Giraffe", "Tiger", "Sheep", "Zebra", "Rabbit", "Shark", "Reindeer"]: currentCategory = "Animals"
        elif properAnswer in ["Star Wars", "Indiana Jones", "Snow White", "Wizard of Oz", "Back to the Future", "Forrest Gump", "Jaws", "Toy Story", "Jurassic Park", "Ghostbusters"]: currentCategory = "Movies"
        elif properAnswer in ["Chicago", "Detroit", "New York", "Pittsburgh", "Denver", "Houston", "New Orleans", "San Francisco", "Miami", "Boston"]: currentCategory = "US Cities"
        elif properAnswer in ["Apple", "Popcorn", "Bacon and eggs", "Ice cream", "Cherries", "Cake", "Banana", "Pizza", "Pumpkin Pie", "Hot dogs"]: currentCategory = "Foods"
        elif properAnswer in ["Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche", "Blue Jackets", "Stars", "Red Wings", "Oilers", "Panthers", "Kings", "Wild", "Canadiens", "Predators", "Devils", "Islanders", "Rangers", "Senators", "Flyers", "Penguins", "Sharks", "Blues", "Lightning", "Maple Leafs", "Canucks", "Golden Knights", "Capitals", "Jets", "Kraken"]: currentCategory = "Hockey Teams"
        elif properAnswer in ["University of Wisconsin", "Purdue University", "Northwestern University", "University of Nebraska", "University of Minnesota", "University of Iowa", "University of Illinois", "Rutgers University", "Pennsylvania State University", "Ohio State University", "Michigan State University", "University of Michigan", "University of Maryland", "Indiana University"]: currentCategory = "Big Ten Colleges"
        elif properAnswer in ["Diamondbacks", "Braves", "Orioles", "Red Sox", "White Sox", "Cubs", "Reds", "Indians", "Rockies", "Tigers", "Astros", "Royals", "Angels", "Dodgers", "Marlins", "Brewers", "Twins", "Yankees", "Mets", "Athletics", "Phillies", "Pirates", "Padres", "Giants", "Mariners", "Cardinals", "Rays", "Rangers", "Blue Jays", "Nationals"]: currentCategory = "Baseball Teams"
        elif properAnswer in ["Hawks", "Celtics", "Nets", "Hornets", "Bulls", "Cavaliers", "Mavericks", "Nuggets", "Pistons", "Warriors", "Rockets", "Pacers", "Clippers", "Lakers", "Grizzlies", "Heat", "Bucks", "Timberwolves", "Pelicans", "Knicks", "Thunder", "Magic", "76ers", "Suns", "Blazers", "Kings", "Spurs", "Raptors", "Jazz", "Wizards"]: currentCategory = "Basketball Teams"
        gameHints()
## Start Game
        if " " in properAnswer: found.append(" ")
        lowerAnswer = properAnswer.lower()
        lowerAnswer = lowerAnswer.replace(" ", "")
        if gameHintsActivated == True: print("Game Category: " + currentCategory + "\nGame Hint: " + gameHint)
        else: print("Game Category: " + currentCategory)
        HangmanGame()
    else:
        allWordsUsed = True
        if "disable" in accountOwnedDLC: print("\n\nYou have played all of the available game words.\n\nEnable more DLC in DLC Management to unlock more words.\n\nThank you so much for playing!\n\n")
        else: print("\n\nYou have played all of the available game words.\n\nThank you so much for playing!\n\n")
        if len(usedWordList) >= 86:
            Achievements("Achievement_All_Topics")
            Achievements("Achievement_Progress_100Check")
        print(("-" * 60) + "\n\n\n")
        menuOption = "All Done"
        startMenu("noWords")

def gameHints():
## Find Game Hint
    global gameHint
    if gameHintsActivated == True:
        if currentCategory == "Animals":
            if properAnswer == "Dog": gameHint = "Man's best friend"
            elif properAnswer == "Horse": gameHint = "Racing Animal"
            elif properAnswer == "Cow": gameHint = "Animal to milk"
            elif properAnswer == "Giraffe": gameHint = "Long-necked animal"
            elif properAnswer == "Tiger": gameHint = "Large wild cat"
            elif properAnswer == "Sheep": gameHint = "Woolly animal"
            elif properAnswer == "Zebra": gameHint = "Striped animal"
            elif properAnswer == "Rabbit": gameHint = "Long-eared animal"
            elif properAnswer == "Shark": gameHint = "Predatory fish"
            elif properAnswer == "Reindeer": gameHint = "Arctic animal"
        elif currentCategory == "Movies":
            if properAnswer == "Star Wars": gameHint = "No. I am your father."
            elif properAnswer == "Indiana Jones": gameHint = "It belongs in a museum!"
            elif properAnswer == "Snow White": gameHint = "Who's the fairest of them all?"
            elif properAnswer == "Wizard of Oz": gameHint = "There's no place like home."
            elif properAnswer == "Back to the Future": gameHint = "When this baby hits 88 miles per hour."
            elif properAnswer == "Forrest Gump": gameHint = "Life is a box of chocolates."
            elif properAnswer == "Jaws": gameHint = "You're gonna need a bigger boat."
            elif properAnswer == "Toy Story": gameHint = "To infinity, and beyond!"
            elif properAnswer == "Jurassic Park": gameHint = "Life uh... finds a way."
            elif properAnswer == "Ghostbusters": gameHint = "Who you gonna call?"
        elif currentCategory == "US Cities":
            if properAnswer == "Chicago": gameHint = "Windy City"
            elif properAnswer == "Detroit": gameHint = "Motor City"
            elif properAnswer == "New York": gameHint = "The Big Apple"
            elif properAnswer == "Pittsburgh": gameHint = "Steel City"
            elif properAnswer == "Denver": gameHint = "Mile High City"
            elif properAnswer == "Houston": gameHint = "Space City"
            elif properAnswer == "New Orleans": gameHint = "The Big Easy"
            elif properAnswer == "San Francisco": gameHint = "The Golden City"
            elif properAnswer == "Miami": gameHint = "The Magic City"
            elif properAnswer == "Boston": gameHint = "The Hub"
        elif currentCategory == "Foods":
            if properAnswer == "Apple": gameHint = "One a day keeps the doctor away."
            elif properAnswer == "Popcorn": gameHint = "Common movie snack"
            elif properAnswer == "Bacon and eggs": gameHint = "Common breakfast food"
            elif properAnswer == "Ice cream": gameHint = "Popular summer treat"
            elif properAnswer == "Cherries": gameHint = "Michigan grown fruit"
            elif properAnswer == "Cake": gameHint = "Dessert for birthdays"
            elif properAnswer == "Banana": gameHint = "Monkeys enjoy eating this"
            elif properAnswer == "Pizza": gameHint = "Cheese and pepperoni"
            elif properAnswer == "Pumpkin Pie": gameHint = "Common at Thanksgiving dinner"
            elif properAnswer == "Hot dogs": gameHint = "Popular ballpark food"
        elif currentCategory == "Hockey Teams":
            if properAnswer == "Ducks": gameHint = "Anaheim"
            elif properAnswer == "Coyotes": gameHint = "Arizona"
            elif properAnswer == "Bruins": gameHint = "Boston"
            elif properAnswer == "Sabres": gameHint = "Buffalo"
            elif properAnswer == "Flames": gameHint = "Calgary"
            elif properAnswer == "Hurricanes": gameHint = "Carolina"
            elif properAnswer == "Blackhawks": gameHint = "Chicago"
            elif properAnswer == "Avalanche": gameHint = "Colorado"
            elif properAnswer == "Blue Jackets": gameHint = "Columbus"
            elif properAnswer == "Stars": gameHint = "Dallas"
            elif properAnswer == "Red Wings": gameHint = "Detroit"
            elif properAnswer == "Oilers": gameHint = "Edmonton"
            elif properAnswer == "Panthers": gameHint = "Florida"
            elif properAnswer == "Kings": gameHint = "Los Angeles"
            elif properAnswer == "Wild": gameHint = "Minnesota"
            elif properAnswer == "Canadiens": gameHint = "Montreal"
            elif properAnswer == "Predators": gameHint = "Nashville"
            elif properAnswer == "Devils": gameHint = "New Jersey"
            elif properAnswer == "Islanders": gameHint = "New York"
            elif properAnswer == "Rangers": gameHint = "New York"
            elif properAnswer == "Senators": gameHint = "Ottawa"
            elif properAnswer == "Flyers": gameHint = "Philadelphia"
            elif properAnswer == "Penguins": gameHint = "Pittsburgh"
            elif properAnswer == "Sharks": gameHint = "San Jose"
            elif properAnswer == "Blues": gameHint = "St. Louis"
            elif properAnswer == "Lightning": gameHint = "Tampa Bay"
            elif properAnswer == "Maple Leafs": gameHint = "Toronto"
            elif properAnswer == "Canucks": gameHint = "Vancouver"
            elif properAnswer == "Golden Knights": gameHint = "Vegas"
            elif properAnswer == "Capitals": gameHint = "Washington"
            elif properAnswer == "Jets": gameHint = "Winnipeg"
            elif properAnswer == "Kraken": gameHint = "Seattle"
        elif currentCategory == "Big Ten Colleges":
            if properAnswer == "University of Wisconsin": gameHint = "Badgers"
            elif properAnswer == "Purdue University": gameHint = "Boilermakers"
            elif properAnswer == "Northwestern University": gameHint = "Wildcats"
            elif properAnswer == "University of Nebraska": gameHint = "Cornhuskers"
            elif properAnswer == "University of Minnesota": gameHint = "Golden Gophers"
            elif properAnswer == "University of Iowa": gameHint = "Hawkeyes"
            elif properAnswer == "University of Illinois": gameHint = "Fighting Illini"
            elif properAnswer == "Rutgers University": gameHint = "Scarlet Knights"
            elif properAnswer == "Pennsylvania State University": gameHint = "Nittany Lions"
            elif properAnswer == "Ohio State University": gameHint = "Buckeyes"
            elif properAnswer == "Michigan State University": gameHint = "Spartans"
            elif properAnswer == "University of Michigan": gameHint = "Wolverines"
            elif properAnswer == "University of Maryland": gameHint = "Terrapins"
            elif properAnswer == "Indiana University": gameHint = "Hoosiers"
        elif currentCategory == "Baseball Teams":
            if properAnswer == "Diamondbacks": gameHint = "Arizona"
            elif properAnswer == "Braves": gameHint = "Atlanta"
            elif properAnswer == "Orioles": gameHint = "Baltimore"
            elif properAnswer == "Red Sox": gameHint = "Boston"
            elif properAnswer == "White Sox": gameHint = "Chicago"
            elif properAnswer == "Cubs": gameHint = "Chicago"
            elif properAnswer == "Reds": gameHint = "Cincinnati"
            elif properAnswer == "Indians": gameHint = "Cleveland"
            elif properAnswer == "Rockies": gameHint = "Colorado"
            elif properAnswer == "Tigers": gameHint = "Detroit"
            elif properAnswer == "Astros": gameHint = "Houston"
            elif properAnswer == "Royals": gameHint = "Kansas"
            elif properAnswer == "Angels": gameHint = "Los Angeles"
            elif properAnswer == "Dodgers": gameHint = "Los Angeles"
            elif properAnswer == "Marlins": gameHint = "Miami"
            elif properAnswer == "Brewers": gameHint = "Milwaukee"
            elif properAnswer == "Twins": gameHint = "Minnesota"
            elif properAnswer == "Yankees": gameHint = "New York"
            elif properAnswer == "Mets": gameHint = "New York"
            elif properAnswer == "Athletics": gameHint = "Oakland"
            elif properAnswer == "Phillies": gameHint = "Philadelphia"
            elif properAnswer == "Pirates": gameHint = "Pittsburgh"
            elif properAnswer == "Padres": gameHint = "San Diego"
            elif properAnswer == "Giants": gameHint = "San Francisco"
            elif properAnswer == "Mariners": gameHint = "Seattle"
            elif properAnswer == "Cardinals": gameHint = "St. Louis"
            elif properAnswer == "Rays": gameHint = "Tampa Bay"
            elif properAnswer == "Rangers": gameHint = "Texas"
            elif properAnswer == "Blue Jays": gameHint = "Toronto Blue"
            elif properAnswer == "Nationals": gameHint = "Washington"
        elif currentCategory == "Basketball Teams":
            if properAnswer == "Hawks": gameHint = "Atlanta"
            elif properAnswer == "Celtics": gameHint = "Boston"
            elif properAnswer == "Nets": gameHint = "Brooklyn"
            elif properAnswer == "Hornets": gameHint = "Charlotte"
            elif properAnswer == "Bulls": gameHint = "Chicago"
            elif properAnswer == "Cavaliers": gameHint = "Cleveland"
            elif properAnswer == "Mavericks": gameHint = "Dallas"
            elif properAnswer == "Nuggets": gameHint = "Denver"
            elif properAnswer == "Pistons": gameHint = "Detroit"
            elif properAnswer == "Warriors": gameHint = "Golden State"
            elif properAnswer == "Rockets": gameHint = "Houston"
            elif properAnswer == "Pacers": gameHint = "Indiana"
            elif properAnswer == "Clippers": gameHint = "Los Angeles"
            elif properAnswer == "Lakers": gameHint = "Los Angeles"
            elif properAnswer == "Grizzlies": gameHint = "Memphis"
            elif properAnswer == "Heat": gameHint = "Miami"
            elif properAnswer == "Bucks": gameHint = "Milwaukee"
            elif properAnswer == "Timberwolves": gameHint = "Minnesota"
            elif properAnswer == "Pelicans": gameHint = "New Orleans"
            elif properAnswer == "Knicks": gameHint = "New York"
            elif properAnswer == "Thunder": gameHint = "Oklahoma City"
            elif properAnswer == "Magic": gameHint = "Orlando"
            elif properAnswer == "76ers": gameHint = "Philadelphia"
            elif properAnswer == "Suns": gameHint = "Phoenix"
            elif properAnswer == "Blazers": gameHint = "Portland Trail"
            elif properAnswer == "Kings": gameHint = "Sacramento"
            elif properAnswer == "Spurs": gameHint = "San Antonio"
            elif properAnswer == "Raptors": gameHint = "Toronto"
            elif properAnswer == "Jazz": gameHint = "Utah"
            elif properAnswer == "Wizards": gameHint = "Washington"
        else:
            print("Game Error: (Restarting game)...")
            gameStart()
    else: gameHint = "No Hints"

def HangmanGame():
## Start Game
    global firstTry, found, gameLives, usedLetters, userGuess
## Lives Left
    if gameLives <= 0:
        print("----|\n|   0\n|  \|/\n|   |\n|   ^\n")
        print("You ran out of lives.\n\n\nThe letters you used were: " + str(usedLetters) + "\nThe correct answer was: " + properAnswer + "\n\n")
        playAgain("Incorrect")
## Whole Word Guessed
    else:
        if len(set(properAnswer.lower())) == len(found):
            if 3 - gameLives == 1: print("Nice Job! You guessed the word correctly.\n\n\nYou only used " + str(3 - gameLives) + " life.\nThe letters you used were: " + str(usedLetters) + "\nThe answer was: " + properAnswer + "\n\n")
            else: print("Nice Job! You guessed the word correctly.\n\n\nYou only used " + str(3 - gameLives) + " lives.\nThe letters you used were: " + str(usedLetters) + "\nThe answer was: " + properAnswer + "\n\n")
            playAgain("Correct")
            return
        else:
            if firstTry == True: print("\n\n")
            if gameLives == 1: print("----|\n|   0\n|  \|/\n|   \n|   ") 
            elif gameLives == 2: print("----|\n|   0\n|   \n|   \n|   ") 
            elif gameLives == 3: print("----|\n|   \n|   \n|   \n|   ") 
            print("\nLives Remaining: " + str(gameLives) + "\n")
            print(" ".join(i if i in found else '_' for i in properAnswer.lower()))
## Show Used Letters
        if firstTry == False: print("\nLetters that you have used: " + str(usedLetters) + "\n")
        userGuess = input(str("\nWhat letter would you like to guess? ")).replace(" ", "")
        if userGuess.lower() not in ["quit", "exit", "terminate", "menu", "mainmenu", "back"]:
            clear()
            print("-" * 60)
            if gameHintsActivated == True: print("Game Category: " + currentCategory + "\nGame Hint: " + gameHint + "\n")
            else: print("Game Category: " + currentCategory + "\n")
## Letter Checks
        if userGuess.isalpha() == False:
            print("Please type a letter from the alphabet.\n\n")
            Achievements("Achievement_Alphabet")
            if punishmentMode == True: gameLives -= 1
            HangmanGame()
        elif userGuess.lower() in ["quit", "exit", "terminate"]:
            Achievements("Achievement_Terminate")
            accountLogin("quit")
        elif userGuess.lower() in ["menu", "mainmenu", "back"]:
            print("\n\n\nExiting to the menu...")
            clear()
            startMenu("")
        elif userGuess.lower() in ["solve", "answer"]:
            userGuess = ""
            solveWord()
            return
        elif userGuess.lower() == lowerAnswer:
            if smartWordDetector == True: solveWord()
            else:
                print("You can only guess one letter at a time.\nYou can type 'solve' if you know the entire word/phrase.\n\n")
                if punishmentMode == True: gameLives -= 1
                HangmanGame()
        elif len(userGuess) != 1 and userGuess.lower() not in ["quit", "exit", "terminate", "menu", "mainmenu", "quit", "exit", "terminate"]:
            print("You can only guess one letter at a time.\nYou can type 'solve' if you know the entire word/phrase.\n\n")
            if punishmentMode == True: gameLives -= 1
            HangmanGame()
## Letter Already Used
        else:
            if userGuess.lower() in usedLetters:
                print("\nYou already tried this letter.\n\n")
                Achievements("Achievement_Same_Letter")
                if punishmentMode == True: gameLives -= 1
                HangmanGame()
## Letter in Word
            else:
                firstTry = False
                usedLetters.append(userGuess.lower())
                if userGuess.lower() in lowerAnswer:
                    print("\nYes, that is in the word.\n\n")
                    found.append(userGuess.lower())
                    HangmanGame()
                else:
                    gameLives -= 1
                    print("\nNo, that is not in the word.\n\n")
                    HangmanGame()

def solveWord():
## Solve Entire Word
    global userGuess
    print(" ".join(i if i in found else '_' for i in properAnswer.lower()))
    if userGuess == "": userGuess = input(str("\n\nYou only get one chance!\n\nWhat word/phrase do you think it is? "))
    userGuess = userGuess.replace(" ", "")
    userGuess = userGuess.lower()
    if userGuess == lowerAnswer:
        if 3 - gameLives == 1: print("\n\nWow! You got the word right.\n\n\nYou only used " + str(3 - gameLives) + " life.")
        else: print("\n\nWow! You got the word right.\n\n\nYou only used " + str(3 - gameLives) + " lives.")
        if not usedLetters: print("You didn't use any letters.\nThe answer was: " + properAnswer + "\n\n")
        else: print("The letters you used were: " + str(usedLetters) + "\nThe answer was: " + properAnswer + "\n\n")
        if not usedLetters: Achievements("Achievement_Solve_Correct_No_Help")
        else: Achievements("Achievement_Solve_Correct")
        playAgain("Correct")
    else:
        if not usedLetters: print("\n\nSorry, that was not the word.\nYou didn't use any letters.\nThe correct answer was: " + properAnswer + "\n\n")
        else: print("\n\nSorry, that was not the word.\n\n\nThe letters you used were: " + str(usedLetters) + "\nThe correct answer was: " + properAnswer + "\n\n")
        Achievements("Achievement_Solve_Wrong")
        playAgain("Incorrect")

def playAgain(gameResult):
## Play Again
    global availablePossibleAnswers, oneGamePlayed, usedWordList
    oneGamePlayed = True
    if gameResult != "Retry":
        availablePossibleAnswers.remove(properAnswer)
        if deactivateFileOpening == False:
            pickle.dump(availablePossibleAnswers, open(currentAccountPath + "\\availablePossibleAnswers.p", "wb"))
            try: usedWordList = pickle.load(open(currentAccountPath + "\\usedWordList.p", "rb"))
            except OSError: usedWordList = []
    if properAnswer not in usedWordList and deactivateFileOpening == False:
        usedWordList.append(properAnswer)
        if currentCategory == "Animals": Achievements("Achievement_Progress_Animals")
        elif currentCategory == "Movies": Achievements("Achievement_Progress_Movies")
        elif currentCategory == "US Cities": Achievements("Achievement_Progress_USCities")
        elif currentCategory == "Foods": Achievements("Achievement_Progress_Foods")
        elif currentCategory == "Hockey Teams": Achievements("Achievement_Progress_HockeyTeams")
        elif currentCategory == "Big Ten Colleges": Achievements("Achievement_Progress_BigTenColleges")
        elif currentCategory == "Baseball Teams": Achievements("Achievement_Progress_BaseballTeams")
        elif currentCategory == "Basketball Teams": Achievements("Achievement_Progress_BasketballTeams")
        if gameResult == "Correct": Achievements("Achievement_Progress_WinStreak")
        if deactivateFileOpening == False: pickle.dump(usedWordList, open(currentAccountPath + "\\usedWordList.p", "wb"))
    if gameResult == "Correct":
        if gameHintsActivated == True: Achievements("Achievement_Winner")
        else: Achievements("Achievement_Hard_Mode")
        if gameLives < 2: Achievements("Achievement_Close_Call")
    elif gameResult == "Incorrect": Achievements("Achievement_Progress_LoseStreak")
    Achievements("Achievement_Progress_100Check")
    againAnswer = input(str("Would you like to play another game or return to the menu? (Yes/No/Menu) ")).replace(" ", "")
    if  againAnswer.lower() in ["y", "yes", "next"]:
        Achievements("Achievement_Keep_Playing")
        gameStart()
    elif againAnswer.lower() in ["n", "no"]:
        print("\n\n\n\nThanks so much for playing!\n")
        Achievements("Achievement_Stop_Playing")
        accountLogin("quit")
    elif againAnswer.lower() in ["m", "menu", "mainmenu"]:
        clear()
        startMenu("")
    else:
        print("\n\nPlease type Yes/No/Menu\n\n")
        playAgain("Retry")


## Start System
gameSetup()