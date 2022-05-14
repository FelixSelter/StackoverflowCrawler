from re import search
from sqlite3 import connect

from bs4 import BeautifulSoup
from htmlmin import minify

if __name__ == "__main__":
    db_source = connect("raw-so-data.db")
    db_target = connect("rawdata.db")
    cursor_source = db_source.cursor()
    cursor_target = db_target.cursor()

    # Create tables
    cursor_target.execute("""
        CREATE TABLE IF NOT EXISTS html (
            id INTEGER,
            html TEXT
            )
    """)
    cursor_target.execute("""
           CREATE TABLE IF NOT EXISTS soitems (
               id INTEGER,
               htmlID INTEGER
               )
       """)

    # Get last processed
    currentID: int = cursor_target.execute("""
           SELECT MAX(id)
           FROM soitems
           """).fetchone()[0] or 0

    # Process
    while True:
        currentID += 1
        if currentID % 100 == 0:
            print(f"Processing: {currentID}")

        # Fetch new data
        data = cursor_source.execute("""
           SELECT * FROM rawdata WHERE id = ?
           """, [currentID]).fetchone()
        if data is None:
            break

        if currentID != data[0]:
            raise Exception("Missing data")

        html = BeautifulSoup(data[1], "html.parser")

        htmlID = search(r"https://stackoverflow\.com/questions/(\d+)/",
                        html.find("meta", {"property": "og:url"})["content"])

        # Edge case 136 Posts that have been moved from SO to other stack exchange sites will be skipped
        # The converter will then treat them as deleted
        if htmlID is None:
            continue
        htmlID = htmlID.group(1)

        # Write to db
        cursor_target.execute("""
           INSERT INTO soitems (id, htmlID)
           VALUES (?, ?)
        """, [currentID, htmlID])
        cursor_target.execute("""
        SELECT * FROM html
        WHERE id = ?
        """, [htmlID])
        if cursor_target.fetchone() is None:
            cursor_target.execute("""
            INSERT INTO html (id, html)
            VALUES (?, ?)
            """, [htmlID, minify(data[1])])
        db_target.commit()
