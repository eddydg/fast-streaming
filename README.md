# fast-streaming
Very simple Python script for personal usage :
 - Select video via sftp (or provide directly an URL/Torrent/Magnet/...)
 - Downloads it with aria2c with multiple connections at the same time to bypass some possible speed limit,
 - Starts to download blocks from the begining to start streaming right away,
 - Download subtitles
 - Opens it with VLC.

## TODO List
 - [x] Enter video URL from both argv and input
 - [x] Get Subtitles from Subliminal
 - [x] Browse via SFTP and select video with a UI
