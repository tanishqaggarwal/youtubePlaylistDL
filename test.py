from bs4 import BeautifulSoup
import urllib.request

vid = "http://www.youtube.com/watch?v=GPtYcAJPxlQ"

def getPublishingYear(video_url):
    text = BeautifulSoup(urllib.request.urlopen(video_url).read(), "lxml")
    return text.findAll("strong", { "class" : "watch-time-text" })[0].string[-4:]

print(getPublishingYear(vid))