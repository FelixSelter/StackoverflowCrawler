from datetime import datetime
from os import times
from re import S


def getAnswerStats(html, id, status):
    answer = html.find(
        "div", {"id": f"answer-{id}"})
    if answer is None:
        return None, None, "deleted", None, None, None

    accepted = False
    if "accepted-answer" in answer["class"]:
        accepted = True

    score = answer["data-score"]

    editTime, creationTime = None, None
    timestats = answer.find_all("div", {"class": "user-info"})

    for timestat in timestats:
        wiki = True if not timestat.find(
            "span", {"class": "community-wiki"}) is None else False

        if wiki is False:
            time = timestat.find(
                "span", {"class": "relativetime"})
            if(time.previous_sibling.strip() == "answered"):
                creationTime = datetime.fromisoformat(
                    time["title"][0:-1].replace(" ", "T"))
            elif time.previous_sibling.strip() == "edited":
                editTime = datetime.fromisoformat(
                    time["title"][0:-1].replace(" ", "T"))

    return creationTime, editTime, status, accepted, score, wiki
