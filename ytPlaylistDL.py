#!/usr/bin/env python3

import urllib.request
import urllib.error

import re
import sys
import time
import os

from pytube import YouTube

class progressBar:
    def __init__(self, barlength=25):
        self.barlength = barlength
        self.position = 0
        self.longest = 0

    def print_progress(self, cur, total, start):
        currentper = cur / total
        elapsed = int(time.clock() - start) + 1
        curbar = int(currentper * self.barlength)
        bar = '\r[' + '='.join(['' for _ in range(curbar)])  # Draws Progress
        bar += '>'
        bar += ' '.join(['' for _ in range(int(self.barlength - curbar))]) + '] '  # Pads remaining space
        bar += bytestostr(cur / elapsed) + '/s '  # Calculates Rate
        bar += getHumanTime((total - cur) * (elapsed / cur)) + ' left'  # Calculates Remaining time
        if len(bar) > self.longest:  # Keeps track of space to over write
            self.longest = len(bar)
            bar += ' '.join(['' for _ in range(self.longest - len(bar))])
        sys.stdout.write(bar)

    def print_end(self, *args):  # Clears Progress Bar
        sys.stdout.write('\r{0}\r'.format((' ' for _ in range(self.longest))))

def getHumanTime(sec):
    if sec >= 3600:  # Converts to Hours
        return '{0:d} hour(s)'.format(int(sec / 3600))
    elif sec >= 60:  # Converts to Minutes
        return '{0:d} minute(s)'.format(int(sec / 60))
    else:            # No Conversion
        return '{0:d} second(s)'.format(int(sec))

def bytestostr(bts):
    bts = float(bts)
    if bts >= 1024 ** 4:    # Converts to Terabytes
        terabytes = bts / 1024 ** 4
        size = '%.2fTb' % terabytes
    elif bts >= 1024 ** 3:  # Converts to Gigabytes
        gigabytes = bts / 1024 ** 3
        size = '%.2fGb' % gigabytes
    elif bts >= 1024 ** 2:  # Converts to Megabytes
        megabytes = bts / 1024 ** 2
        size = '%.2fMb' % megabytes
    elif bts >= 1024:       # Converts to Kilobytes
        kilobytes = bts / 1024
        size = '%.2fKb' % kilobytes
    else:                   # No Conversion
        size = '%.2fb' % bts
    return size

def getPageHtml(url):
    try:
        yTUBE = urllib.request.urlopen(url).read()
        return str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)
        exit(1)

def getPlaylistUrlID(url):
    if 'list=' in url:
        eq_idx = url.index('=') + 1
        pl_id = url[eq_idx:]
        if '&' in url:
            amp = url.index('&')
            pl_id = url[eq_idx:amp]
        return pl_id   
    else:
        print(url, "is not a youtube playlist.")
        exit(1)

def getFinalVideoUrl(vid_urls):
    final_urls = []
    for vid_url in vid_urls:
        url_amp = len(vid_url)
        if '&' in vid_url:
            url_amp = vid_url.index('&')
        final_urls.append('http://www.youtube.com/' + vid_url[:url_amp])
    return final_urls

def getPlaylistVideoUrls(page_content, url):
    playlist_id = getPlaylistUrlID(url)

    vid_url_pat = re.compile(r'watch\?v=\S+?list=' + playlist_id)
    vid_url_matches = list(set(re.findall(vid_url_pat, page_content)))

    if vid_url_matches:
        final_vid_urls = getFinalVideoUrl(vid_url_matches)
        print("Found",len(final_vid_urls),"videos in playlist.")
        printUrls(final_vid_urls)
        return final_vid_urls
    else:
        print('No videos found.')
        exit(1)



#function added to get audio files along with the video files from the playlist

def download_Video_Audio(path, vid_url, file_no):
    try:
        yt = YouTube(vid_url)
    except Exception as e:
        print("Error:", str(e), "- Skipping Video with url '"+vid_url+"'.")
        return

    try:  # Tries to find the video in 720p
        video = yt.get('mp4', '720p')
    except Exception:  # Sorts videos by resolution and picks the highest quality video if a 720p video doesn't exist
        video = sorted(yt.filter("mp4"), key=lambda video: int(video.resolution[:-1]), reverse=True)[0]
    print("downloading", yt.filename+" Video and Audio...")

    #Let's clean up the file name a bit
    dash_index = yt.filename.find("-")
    parenthetical_index = yt.filename.find("(")
    if parenthetical_index == -1:
        parenthetical_index = yt.filename.find("[")

    new_filename = yt.filename[dash_index + 1 : parenthetical_index - 1]
    author = yt.filename[:dash_index]
    if author == "":
        author = "Unknown"

    pathslash = path + "/"

    try:
        if os.path.isfile(pathslash + new_filename + ".mp3"):
            raise FileNotFoundError()

        bar = progressBar()
        video.download(path, on_progress=bar.print_progress, on_finish=bar.print_end)
        print("successfully downloaded", yt.filename, "!")
    except FileNotFoundError:
        print(yt.filename, "already exists in this directory! Skipping video...")

    try:
        aud = 'ffmpeg -i \"'+pathslash+str(yt.filename)+'.mp4\"'+' \"'+pathslash+str(file_no)+'.wav\"'
        thumbnail = 'ffmpeg -i \"' + pathslash + str(yt.filename) + '.mp4\" -ss 00:00:10 -vframes 1 \"' + pathslash + str(file_no) + '.png\"'
        final_audio ='lame --ta \"' + author + '\" --ti \"' + pathslash + str(file_no) + '.png\" \"' + pathslash + str(file_no)+'.wav\"'+' \"'+ pathslash + str(new_filename)+'.mp3\"'

        os.system(aud)
        os.system(thumbnail)
        os.system(final_audio)
        os.remove(pathslash + str(file_no)+'.png')
        os.remove(pathslash + str(yt.filename)+'.mp4')
        os.remove(pathslash + str(file_no)+'.wav')
        print("sucessfully converted" ,new_filename, "into audio!")
    except OSError:
        print(yt.filename, "There is some problem with the file names...")

def printUrls(vid_urls):
    for url in vid_urls:
        print(url)
        time.sleep(0.04)
        
if __name__ == '__main__':
    url = "https://www.youtube.com/playlist?list=PLfvxCUZ9EspopJOS8XhYrRJXLlPTadp5z"
    directory = "/Users/Tanishq/Music/iTunes/iTunes Media/Music/YouTube Playlist"

    # make directory if dir specified doesn't exist
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as e:
        print(e.reason)
        exit(1)

    if not url.startswith("http"):
        url = 'https://' + url

    playlist_page_content = getPageHtml(url)
    vid_urls_in_playlist = getPlaylistVideoUrls(playlist_page_content, url)

    # downloads videos and audios
    for i,vid_url in enumerate(vid_urls_in_playlist):
        download_Video_Audio(directory, vid_url, i)
        time.sleep(1)