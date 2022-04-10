from datetime import datetime
from os import times
import re


def getAnswerStats(html, id, status):
    answer = html.find(
        "div", {"id": f"answer-{id}"})
    if answer is None:
        return None, None, "deleted", None, None, None, None, None

    accepted = False
    if "accepted-answer" in answer["class"]:
        accepted = True

    score = answer["data-score"]

    editTime, creationTime, author, editor = None, None, None, None
    timestats = answer.find_all("div", {"class": "user-info"})
    if len(timestats) > 2:
        raise Exception("More than two timestats")

    for timestat in timestats:
        wiki = True if not timestat.find(
            "span", {"class": "community-wiki"}) is None else False

        if wiki is False:
            time = timestat.find(
                "span", {"class": "relativetime"})

            # edgecase 364
            action = time.previous_sibling
            if action is None:
                action = time.parent.previous_sibling
            action = action.strip()

            if(action == "answered"):
                creationTime = datetime.fromisoformat(
                    time["title"][0:-1].replace(" ", "T"))
                details = timestat.find(
                    "div", {"class": "user-details"})
                author = details.find("a")
                author = author.text if author is not None else details.contents[0].strip(
                )

            elif action == "edited":
                editTime = datetime.fromisoformat(
                    time["title"][0:-1].replace(" ", "T"))
                details = timestat.find(
                    "div", {"class": "user-details"})
                editor = details.find("a")
                editor = editor.text if editor is not None else details.contents[0].strip(
                )

    return creationTime, editTime, status, accepted, score, wiki, author, editor
