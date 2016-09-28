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

    # Wait for the video to be created
    while not os.path.exists(videoPath):
        time.sleep(1)

    time.sleep(1)


    # Quick and simple subtitle download without checking its format
    """
    subliminalProcess = subprocess.Popen(
        ["subliminal", "download", "-l", "en", "-s", videoPath],
        stdout=sys.stdout,
        stderr=sys.stderr)
    """

    region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})
    video = scan_video(videoPath)
    print("Video info - Codec: " + video.video_codec + " - Release: " + video.release_group)
    subtitles = download_best_subtitles([video], {Language(languages[0])})

    hasFoundSubtitle = False
    if len(subtitles) > 0:
        print("A subtitle has been found!")
        hasFoundSubtitle = True
        save_subtitles(video, subtitles[video])
    else:
        print("No subtitles found.")

    subtitlePath = os.path.splitext(videoPath)[0] + "." + languages[0][:2] + ".srt"


    if hasFoundSubtitle and os.path.exists(subtitlePath):
        vlcProcess = subprocess.Popen(["vlc", "--sub-file=" + subtitlePath, videoPath])
    else:
        vlcProcess = subprocess.Popen(["vlc", videoPath])

    vlcProcess.wait()
    print("VLC process finished.")
    print("Terminating aria2c.")
    ariaProcess.terminate()

    while True:
        res = input("Move the video to the (t)rash, (d)elete or do (n)othing? (default 'd') [t/d/n] ")

        if (res == "t"):
            send2trash(videoPath)
            if os.path.exists(subtitlePath):
                send2trash(subtitlePath)
            sys.exit(0)
        elif (res == "n"):
            sys.exit(0)
        elif (res == "d" or res == ""):
            os.remove(videoPath)
            if os.path.exists(subtitlePath):
                send2trash(subtitlePath)
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
