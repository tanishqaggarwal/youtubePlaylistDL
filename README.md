# Youtube Song Downloader
A simple script to download all songs in a Youtube playlist. It adds relevant ID3 tags and album art through web scraping.

### Requirements:


#####**This script needs Python 3.4.1+**

```bash
$ brew install ffmpeg
$ pip3 install pytube bs4 Request
```

### Usage:

Update the download directory and playlist URL in `main.py`, then run the downloader using

```bash
$ python3 main.py
```