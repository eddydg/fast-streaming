import sys
import subprocess
import time
import os
import urllib.parse

import tempfile
from send2trash import send2trash
from babelfish import Language
from subliminal import *

def main(filePath):
    targetPath = tempfile.gettempdir()
    filename = os.path.basename(filePath).split("?")[0]
    videoPath = urllib.parse.unquote(os.path.join(targetPath, filename))
    languages = ["eng"]

    ariaProcess = subprocess.Popen(
        ["aria2c", "-x 8", "--file-allocation=none", "--continue=true", "--stream-piece-selector=inorder", "--dir=" + targetPath, filePath],
        stdout=sys.stdout,
        stderr=sys.stderr)

    time.sleep(2)

    """
    subliminalProcess = subprocess.Popen(
        ["subliminal", "download", "-l", "en", "-s", videoPath],
        stdout=sys.stdout,
        stderr=sys.stderr)
    """

    region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})
    video = scan_video(videoPath)
    print(video.video_codec)
    print(video.release_group)
    subtitles = download_best_subtitles([video], {Language(languages[0])})
    if len(subtitles) > 0:
        print("A subtitle has been found!")
        save_subtitles(video, subtitles[video])
    else:
        print("No subtitles found.")

    subtitle_path = os.path.splitext(videoPath)[0] + "." + languages[0][:2] + ".srt"

    # Let it load a bit
    time.sleep(5)

    vlcProcess = subprocess.Popen(["vlc", "--sub-file=" + subtitle_path, videoPath])

    vlcProcess.wait()
    print("VLC process finished.")
    print("Terminating aria2c.")
    ariaProcess.terminate()

    while True:
        res = input("Move the video to the (t)rash, (d)elete or do (n)othing? (default 'd') [t/d/n] ")

        if (res == "t"):
            send2trash(videoPath)
            sys.exit(0)
        elif (res == "n"):
            sys.exit(0)
        elif (res == "d" or res == ""):
            os.remove(videoPath)
            sys.exit(0)
        else:
            print("Please enter 't', 'd' or 'n'.")

if __name__ == "__main__":
    while True:
        if len(sys.argv) < 2:
            filePath = input("Enter video URL/Torrent/Magnet: ")
        else:
            filePath = sys.argv[1]

        if filePath:
            main(filePath)
