import json
import sqlite3
import requests
import re
from bs4 import BeautifulSoup


def initDB():
    db = sqlite3.connect("stackoverflow.db")
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stackoverflow
        (
            id     INT PRIMARY KEY,
            type   TEXT,
            status TEXT,
            tags   TEXT
        );
        """)
    return db, cursor


def insertData(id: int, type: str, status: str, tags):
    cursor.execute(f"""
                INSERT INTO stackoverflow
                    (id,
                    type,
                    status,
                    tags)
                VALUES
                    ({id},
                    '{type}',
                    '{status}',
                    '{tags}');
                """)


def getStatus(html):
    return "deleted" if html.select('h1.fs-headline1:-soup-contains("Page not found")') else "online"


def getType(r):
    return "question" if r.headers['Location'].startswith(
        f"/questions/{id}") else "answer"


def getTags(html):
    taglist = html.find("div", {"class": "post-taglist"})
    tags = taglist.findChildren("a", {"class": "post-tag"})
    return json.dumps([tag.text for tag in tags])


if __name__ == '__main__':

    db, cursor = initDB()
    id = cursor.execute("SELECT MAX(id) FROM stackoverflow").fetchone()[0] or 0

    while id < 10:
        id += 1
        print(id)
        r = requests.get(f"https://stackoverflow.com/questions/{id}",
                         allow_redirects=False)
        html = BeautifulSoup(requests.get(
            f"https://stackoverflow.com/questions/{id}").text, 'html.parser')

        type = getType(r)
        status = getStatus(html)
        tags = getTags(
            html) if type == "question" and status == "online" else None

        insertData(id, type, status, tags)
        db.commit()

    db.close()
