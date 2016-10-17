import os
import sys
import paramiko
import stat
import configparser
from pick import Picker
from urllib import parse
from enum import Enum

import faststream


configp = configparser.ConfigParser()
if configp.read('config.ini'):
    config = configp['DEFAULT']
else:
    print("config file not found")
    sys.exit()


cakeBase   = config['directURL']
sftpURL    = config['sftpURL']
sftpUser   = config['sftpUser']
sftpPass   = config['sftpPass']
sftpPort   = int(config['sftpPort'])
sftpFolder = config['sftpFolder']

wantedFiles = [e.strip() for e in config['wantedFiles'].split(',')]

ssh = paramiko.SSHClient()

# automatically add keys without requiring human intervention
ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

ssh.connect(sftpURL, username=sftpUser, password=sftpPass, port=sftpPort)
ftp = ssh.open_sftp()


class FileManager():

    def __init__(self):
        self.path = ['torrents', 'series']

    def isDir(self, filename):
        fullPath = self.getCurrentPath(filename)
        statResult = ftp.lstat(fullPath)
        return stat.S_ISDIR(statResult.st_mode)

    def filterExtension(self, items):
        result = []

        for item in items:
            filename, fileextension = os.path.splitext(item)
            if self.isDir(item) or fileextension in wantedFiles:
                result += [item]

        return result

    def getCurrentPath(self, file=None):
        if file is None:
            return '/'.join(self.path)
        else:
            fullpath = self.path + [file]
            return '/'.join(fullpath)

    def select(self, selectedItem):
        itemName = os.path.basename(str(selectedItem))

        if self.isDir(itemName):
            self.path += [itemName]
            return None
        else:
            return cakeBase + '/'.join(self.path[1:]) + '/' + itemName

    def remove(self, filePath):
        try:
            ftp.stat(filePath)
        except IOError as e:
            if e.errno == errno.ENOENT:
                print('Could not delete {}. File does not exist.'.format(filePath))
            else:
                print(str(e))
            return False
        else:
            ftp.remove(filePath)
            return True

    def goUp(self):
        if (len(self.path) > 1):
            self.path.pop()
            return True
        else:
            return False

    def getItems(self, func = None):
        items = ftp.listdir(self.getCurrentPath())
        items = self.filterExtension(items)

        files = []
        folders = []

        for item in items:
            if (self.isDir(item)):
                folders += [item]
            else:
                files += [item]

        if func is not None:
        	fiels = sorted(files, key=func)
        else:
        	files = sorted(files)
        folders = sorted(folders)

        return folders + files

class SelectionType(Enum):
    Manual = 1
    Picker = 2

class FileSelection():

    def __init__(self, fileManager, orderBy=None, selectionType=SelectionType.Picker):
        self.orderBy = orderBy
        self.selectionType = selectionType
        self.fileManager = fileManager

    def switchOrderBy(self, test):
        if self.orderBy is None:
            self.orderBy = lambda x: ftp.stat(self.fileManager.getCurrentPath(x)).st_size
        else:
            self.orderBy = None

        return None, -1

    def askSelection(self, choices):
        selectedItem, selectedIndex = ("", -1)
        currentPath = self.fileManager.getCurrentPath()

        if self.selectionType is SelectionType.Picker:
            picker = Picker(choices, currentPath + " ('q' to quit)")
            picker.register_custom_handler(ord('q'), sys.exit)
            picker.register_custom_handler(ord('o'), self.switchOrderBy)

            selectedItem, selectedIndex = picker.start()

        else:
            while True:
                print(currentPath + " ('q' to quit)")
                for i, choice in enumerate(choices):
                    print("["+str(i)+"] " + choice)
                try:
                    selectedIndex = int(input("Select your choice between 0-" + str(len(choices)-1) + ": "))
                    if selectedIndex < 0 or selectedIndex >= len(choices):
                        print("Invalid choice. Must be between 0-" + str(len(choices)-1) + ".")
                    else:
                        break
                except ValueError:
                    print("Please enter a number.")

        return selectedItem, selectedIndex


fileManager = FileManager()
fileSelection = FileSelection(fileManager)

def browser():
    while True:
        items = fileManager.getItems(fileSelection.orderBy)

        itemsName = []
        for item in items:

            if fileManager.isDir(item):
                itemsName += [os.path.basename(str(item)) + "/"]
            else:
                raw_size = ftp.stat(fileManager.getCurrentPath(item)).st_size
                size = str(round(raw_size / 1024 / 1024)) # Bytes to Megabytes
                itemsName += [os.path.basename(str(item)) + " [" + size + " Mo]"]

        choices = [".."] + itemsName
        selectedItem, selectedIndex = fileSelection.askSelection(choices)

        if selectedItem is None:
        	continue

        if selectedIndex == 0:
            fileManager.goUp()
            continue

        # - 1 for added ".." choice
        selected = fileManager.select(items[selectedIndex - 1])

        if selected:
            return selected, items[selectedIndex - 1]


url, fileName = browser()
fastStreamRet = faststream.main(url, config)

while True:
    res = input("Delete file server-side? (default 'n') [y/n] ")

    if (res == "y"):
        removeRet = fileManager.remove(fileManager.getCurrentPath(fileName))
        sys.exit(0)
    elif (res == "n" or res == ""):
        sys.exit(0)
    else:
        print("Please enter 'y' or 'n'.")
