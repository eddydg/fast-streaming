import os
import sys
import paramiko
import stat
import configparser
from pick import Picker
from urllib import parse

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

    def goUp(self):
        if (len(self.path) > 1):
            self.path.pop()
            return True
        else:
            return False

    def getItems(self):
        items = ftp.listdir(self.getCurrentPath())
        items = self.filterExtension(items)

        files = []
        folders = []

        for item in items:
            if (self.isDir(item)):
                folders += [item]
            else:
                files += [item]

        files = sorted(files)
        folders = sorted(folders)

        return folders + files

def browser():
    fileManager = FileManager()

    while True:
        items = fileManager.getItems()

        itemsName = [os.path.basename(str(x)) for x in items]
        choices = [".."] + itemsName
        picker = Picker(choices, fileManager.getCurrentPath() + " ('q' to quit)")
        picker.register_custom_handler(ord('q'), sys.exit)
        selectedItem, selectedIndex = picker.start()

        if selectedIndex == 0:
            fileManager.goUp()
            continue

        # - 1 for added ".." choice
        selected = fileManager.select(items[selectedIndex - 1])

        if selected:
            return selected


url = browser()
faststream.main(url)