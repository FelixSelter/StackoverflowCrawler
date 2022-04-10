import sqlite3
import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

import questionParser
import answerParser


def initDB():
    db = sqlite3.connect("stackoverflow.db")
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stackoverflow
        (
            id           INT PRIMARY KEY,
            type         TEXT,
            status       TEXT,
            tags         TEXT,
            creationtime TIMESTAMP,
            edittime     TIMESTAMP,
            viewcount    INT,
            accepted     INT,
            score        INT,
            wiki         INT,
            author       TEXT,
            editor       TEXT,
            answers      INT,
            comments     INT
        );
        """)
    return db, cursor


def insertData(id: int, type: str, status: str, tags, creationTime, editTime, viewCount, accepted, score, wiki, author, editor, answers, comments):
    cursor.execute(f"""
        INSERT INTO stackoverflow
            (id,
            type,
            status,
            tags,
            creationtime,
            edittime,
            viewcount,
            accepted,
            score,
            wiki,
            author,
            editor,
            answers,
            comments)
        VALUES
            ({id},
             '{type}',
             '{status}',
             '{tags}',
             '{creationTime}',
             '{editTime}',
             '{viewCount}',
             '{accepted}',
             '{score}',
             '{wiki}',
             '{author}',
             '{editor}',
             '{answers}',
             '{comments}');
                """)


def getStatus(rr):
    return "removed" if rr.status_code == 404 else "online"


def getType(r):
    return "question" if r.headers['Location'].startswith(
        f"/questions/{id}") else "answer"


def requestData(id):
    while True:
        try:
            r = requests.get(f"https://stackoverflow.com/questions/{id}",
                             allow_redirects=False, timeout=10)
            break
        except:
            print(f"Connection error problems with ID: {id}")
            sleep(10)
            continue

    while True:
        try:
            rr = requests.get(
                f"https://stackoverflow.com/questions/{id}", timeout=10)
            break
        except:
            print(f"Connection error problems with ID: {id}")
            sleep(10)
            continue

    return r, rr


def getComments(html, id):
    comments_list = html.find("div", {"id": f"comments-{id}"}
                              ).find("ul", {"class": "comments-list"})
    displayed = len(comments_list.find_all("li"))
    hidden = int(comments_list["data-remaining-comments-count"])
    return displayed+hidden


if __name__ == '__main__':
    RATELIMIT = 90

    db, cursor = initDB()
    id = cursor.execute(
        "SELECT MAX(id) FROM stackoverflow").fetchone()[0] or 0
    starttime = datetime.now()
    requestCounter = 0

    while id < 72000000:
        id += 1
        print(id)

        r, rr = requestData(id)
        requestCounter += 2
        html = BeautifulSoup(rr.text, 'html.parser')
        type, status, tags, creationTime, editTime, viewCount, accepted, score, wiki, author, editor, answers, comments = [
            None for i in range(13)]
        type = getType(r)
        status = getStatus(rr)

        if status == "online":

            if(type == "question"):
                tags = questionParser.getTags(html)
                creationTime, editTime, viewCount = questionParser.getTimeStats(
                    html)
                score = questionParser.getScore(html)
                author, editor, wiki = questionParser.getQuestionStats(html)
                answers = questionParser.getAnswers(html)

            else:
                creationTime, editTime, status, accepted, score, wiki, author, editor = answerParser.getAnswerStats(
                    html, id, status)

            # Recheck: status might have been changed by answerParser.getAnswerStats()
            if status == "online":
                comments = getComments(html, id)

        insertData(id, type, status, tags, creationTime,
                   editTime, viewCount, accepted, score, wiki, author, editor, answers, comments)
        db.commit()

        # Wait because of RATE LIMIT
        if(requestCounter >= RATELIMIT):
            delay = 60 - (datetime.now() - starttime).seconds
            if delay > 0:
                print(f"Waiting {delay} seconds")
                sleep(delay)
            requestCounter = 0
            starttime = datetime.now()

    db.close()
