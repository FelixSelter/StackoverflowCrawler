import json
import re
from datetime import datetime


def getTags(html):
    taglist = html.find("div", {"class": "post-taglist"})
    tags = taglist.findChildren("a", {"class": "post-tag"})
    return json.dumps([tag.text for tag in tags])


def getTimeStats(html):
    statsbar = html.find(
        "div", {"id": "question-header"}).next_sibling.next_sibling
    creationTime = datetime.fromisoformat(statsbar.find("time")["datetime"])
    editTime = datetime.fromisoformat(statsbar.find(
        "a", {"href": "?lastactivity"})["title"][0:-1].replace(" ", "T"))
    viewCount = int(re.search(r"Viewed (.+) times", statsbar.find(
        "div", {"title": re.compile(r"Viewed .+ times")})["title"]).group(1).replace(",", ""))
    return creationTime, editTime, viewCount


def getScore(html):
    return html.find(
        "div", {"id": "question"})["data-score"]
