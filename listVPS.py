import os
import sys
import paramiko
import stat
import configparser
from pick import pick

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
path = 'torrents/' + sftpFolder

def isDir(fullPath):
    statResult = ftp.lstat(fullPath)
    return stat.S_ISDIR(statResult.st_mode)

ssh = paramiko.SSHClient()
# automatically add keys without requiring human intervention
ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

ssh.connect(sftpURL, username=sftpUser, password=sftpPass, port=sftpPort)

ftp = ssh.open_sftp()
files = ftp.listdir('torrents/' + sftpFolder)


class FileManager():

    def __init__(self):
        self.path = ['torrents', 'series']

    def filterExtension(self, items):
        result = []

        for item in items:
            filename, fileextension = os.path.splitext(item)
            if isDir(item) or fileextension in wantedFiles:
                result.append(item)

        return result

    def getCurrentPath(self, file=None):
        if file is None:
            return '/'.join(self.path)
        else:
            fullpath = self.path + [file]
            return '/'.join(fullpath)

    def select(self, selectedItem):
        itemName = os.path.basename(str(selectedItem))
        fullPath = self.getCurrentPath(itemName)

        if isDir(fullPath):
            self.path += [itemName]
            print("Entering dir")
            return False
        else:
            print(cakeBase + '/'.join(self.path[1:]) + '/' + itemName)
            print("Starting script")
            return True

    def up(self):
        if (len(self.path) > 0):
            self.path.pop()
        else:
            print("Cannot go upper!")

    def getItems(self):
        files = ftp.listdir(self.getCurrentPath())
        files = self.filterExtension(files)
        sortedFiles = sorted([self.getCurrentPath(file) for file in files], key=isDir, reverse=True)
        return sortedFiles


fileManager = FileManager()

while True:
    print(fileManager.getCurrentPath())
    items = fileManager.getItems()
    itemsName = [os.path.basename(str(x)) for x in items]
    selectedItem, selectedIndex = pick(itemsName, "choisissez une fichier a stream")

    isOver = fileManager.select(items[selectedIndex])

    if isOver:
        input()
        sys.exit()



