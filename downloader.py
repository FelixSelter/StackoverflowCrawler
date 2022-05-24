import sqlite3
from datetime import datetime
from re import search
from time import sleep

import requests
from bs4 import BeautifulSoup
from htmlmin import minify

db = sqlite3.connect("rawdata.db")
cursor = db.cursor()

cursor.execute("""
       CREATE TABLE IF NOT EXISTS html (
           id INTEGER,
           html TEXT
           )
   """)
cursor.execute("""
          CREATE TABLE IF NOT EXISTS soitems (
              id INTEGER,
              htmlID INTEGER
              )
      """)

RATELIMIT = 35

currentID = cursor.execute(
    "SELECT MAX(id) FROM soitems").fetchone()[0] or 0
start_time = datetime.now()
requestCounter = 0

while currentID < 72000000:
    currentID += 1
    print("Downloading:", currentID)

    while True:
        while True:
            try:
                r = requests.get(f"https://stackoverflow.com/questions/{currentID}", timeout=10)
                break
            except TimeoutError:
                print("TimeoutError")
                sleep(5)
                continue

        requestCounter += 1
        if r.status_code == 429:
            currentID -= 10
            print("RATELIMIT waiting 10 minutes")
            sleep(10 * 60)
            continue

        html = BeautifulSoup(r.text, "html.parser")
        htmlID = search(r"https://stackoverflow\.com/questions/(\d+)/",
                        html.find("meta", {"property": "og:url"})["content"])

        # Edge case 136 Posts that have been moved from SO to other stack exchange sites will be skipped
        # The converter will then treat them as deleted
        if htmlID is None:
            break
        htmlID = htmlID.group(1)

        # Write to db
        cursor.execute("""
                           INSERT INTO soitems (id, htmlID)
                           VALUES (?, ?)
                        """, [currentID, htmlID])
        cursor.execute("""
                        SELECT * FROM html
                        WHERE id = ?
                        """, [htmlID])
        if cursor.fetchone() is None:
            cursor.execute("""
                            INSERT INTO html (id, html)
                            VALUES (?, ?)
                            """, [htmlID, minify(r.text)])
        db.commit()

        # Wait because of RATE LIMIT
        if requestCounter >= RATELIMIT:
            delay = 60 - (datetime.now() - start_time).seconds
            if delay > 0:
                print(f"Waiting {delay} seconds")
                sleep(delay)
            requestCounter = 0
            start_time = datetime.now()

        break  # Exit loop
