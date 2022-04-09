import sqlite3
import requests
from bs4 import BeautifulSoup

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
            viewcount    INT
        );
        """)
    return db, cursor


def insertData(id: int, type: str, status: str, tags, creationTime, editTime, viewCount):
    cursor.execute(f"""
        INSERT INTO stackoverflow
            (id,
            type,
            status,
            tags,
            creationtime,
            edittime,
            viewcount)
        VALUES
            ({id},
             '{type}',
             '{status}',
             '{tags}',
             '{creationTime}',
             '{editTime}',
             '{viewCount}');
                """)


def getStatus(rr):
    return "removed" if rr.status_code == 404 else "online"


def getType(r):
    return "question" if r.headers['Location'].startswith(
        f"/questions/{id}") else "answer"


if __name__ == '__main__':

    db, cursor = initDB()
    id = cursor.execute("SELECT MAX(id) FROM stackoverflow").fetchone()[0] or 0

    while id < 10:
        id += 1
        print(id)
        r = requests.get(f"https://stackoverflow.com/questions/{id}",
                         allow_redirects=False)
        rr = requests.get(
            f"https://stackoverflow.com/questions/{id}")
        html = BeautifulSoup(rr.text, 'html.parser')

        type, status, tags, creationTime, editTime, viewCount = None, None, None, None, None, None
        type = getType(r)
        status = getStatus(rr)

        if status == "online":
            if(type == "question"):
                tags = questionParser.getTags(html)
                creationTime, editTime, viewCount = questionParser.getTimeStats(
                    html)

            else:
                creationTime, editTime, status = answerParser.getTimeStats(
                    html, id, status)

        insertData(id, type, status, tags, creationTime, editTime, viewCount)
        db.commit()

    db.close()
