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


def getQuestionStats(html):
    question = html.find(
        "div", {"id": "question"})

    author, editor = None, None
    timestats = question.find_all("div", {"class": "user-info"})
    if len(timestats) > 2:
        raise Exception("More than two timestats")

    wiki = True if not question.find(
        "span", {"class": "community-wiki"}) is None else False

    if wiki is False:
        for timestat in timestats:
            time = timestat.find(
                "span", {"class": "relativetime"})

            if(time.previous_sibling.strip() == "asked"):
                details = timestat.find(
                    "div", {"class": "user-details"})
                author = details.find("a")
                author = author.text if author is not None else details.contents[0].strip(
                )

            elif time.previous_sibling.strip() == "edited":
                details = timestat.find(
                    "div", {"class": "user-details"})
                editor = details.find("a")
                editor = editor.text if editor is not None else details.contents[0].strip(
                )

    return author, editor, wiki


def getAnswers(html):
    return html.find("h2", {"data-answercount": re.compile("[0-9]+")})["data-answercount"]
