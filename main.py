import sqlite3
import requests
from bs4 import BeautifulSoup
from time import sleep

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
            wiki         INT
        );
        """)
    return db, cursor


def insertData(id: int, type: str, status: str, tags, creationTime, editTime, viewCount, accepted, score, wiki):
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
            wiki)
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
             '{wiki}');
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


if __name__ == '__main__':

    db, cursor = initDB()
    id = cursor.execute("SELECT MAX(id) FROM stackoverflow").fetchone()[0] or 0
    counter = id

    while id < counter + 10:
        id += 1
        print(id)

        r, rr = requestData(id)
        html = BeautifulSoup(rr.text, 'html.parser')
        type, status, tags, creationTime, editTime, viewCount, accepted, score, wiki = None, None, None, None, None, None, None, None, None
        type = getType(r)
        status = getStatus(rr)

        if status == "online":
            if(type == "question"):
                tags = questionParser.getTags(html)
                creationTime, editTime, viewCount = questionParser.getTimeStats(
                    html)
                score = questionParser.getScore(html)

            else:
                creationTime, editTime, status, accepted, score, wiki = answerParser.getAnswerStats(
                    html, id, status)

        insertData(id, type, status, tags, creationTime,
                   editTime, viewCount, accepted, score, wiki)
        db.commit()

    db.close()
