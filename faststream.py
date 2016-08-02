import sys
import subprocess
import time
import os
import urllib.parse
import tempfile
from send2trash import send2trash


if len(sys.argv) < 2:
    sys.exit("Please provide file source")

filepath = sys.argv[1]
targetPath = tempfile.gettempdir()
filename = os.path.basename(filepath).split("?")[0]
videoPath = urllib.parse.unquote(os.path.join(targetPath, filename))

ariaProcess = subprocess.Popen(
    ["aria2c", "-x 8", "--file-allocation=none", "--continue=true", "--stream-piece-selector=inorder", "--dir=" + targetPath, filepath],
    stdout=sys.stdout,
    stderr=sys.stderr)

# Let it load a bit
time.sleep(5)

vlcProcess = subprocess.Popen(["vlc", videoPath])

vlcProcess.wait()
print("VLC process finished.")
print("Terminating aria2c.")
ariaProcess.terminate()

while True:
    res = input("Do you want to move the video to the trash? (default 'y') [y/n] ")

    if (res == "y" or res == ""):
        send2trash(videoPath)
        sys.exit(0)
    elif (res == "n"):
        sys.exit(0)
    else:
        print("Please enter 'y' or 'n'.")
