import json
import re
from datetime import datetime
from logging import info, basicConfig
from re import compile
from sqlite3 import connect

from bs4 import BeautifulSoup

basicConfig(level="ERROR", filename="converter.log")


def createTables():
    cursor_target.execute("""
    CREATE TABLE IF NOT EXISTS questions (
    id INT,
    tags TEXT,
    creationtime DATETIME,
    edittime DATETIME,
    viewcount INT,
    score INT,
    wiki BOOLEAN,
    author TEXT,
    editor TEXT,
    comments INT
    )
    """)

    cursor_target.execute("""
    CREATE TABLE IF NOT EXISTS answers (
    id INT,
    questionID INT,
    accepted BOOLEAN,
    creationtime DATETIME,
    edittime DATETIME,
    score INT,
    wiki BOOLEAN,
    author TEXT,
    editor TEXT,
    comments INT
    )
    """)


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

            if (time.previous_sibling.strip() == "asked"):
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


def getQuestionID(html):
    return html.find("a", {"class": "question-hyperlink"})["href"].split("/")[2]


def getAnswerStats(html, id):
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

            if (action == "answered"):
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

    return creationTime, editTime, accepted, score, wiki, author, editor


def getComments(html, id):
    """Returns the number of comments for a question or answer

    Args:
        html (bs4 document): The Beautiful Soup 4 document of the question page.
        id (int): The id of eather question or answer that should be parsed.

    Returns:
        int: The amount of comments
    """

    comments_list = html.find("div", {"id": f"comments-{id}"})
    if (comments_list is None):  # Edgecase 2366 Merged questions
        return -1

    comments_list = comments_list.find(
        "ul", {"class": "comments-list"})
    displayed = len(comments_list.find_all("li"))
    hidden = int(comments_list["data-remaining-comments-count"])
    return displayed + hidden


def parseItem(id, rawhtml):
    """
    Ignores all deleted

    Args:
        id (int): The id of the question or answer
        rawhtml (string): The html code of the website
    """
    html = BeautifulSoup(rawhtml, "html.parser")
    online = html.find(
        "a", {"href": "/help/deleted-questions"}) == None

    if online:  # Ignore offline
        isQuestion = not online or not html.find("a",
                                                 {"class": "question-hyperlink",
                                                  "href": compile(f'/questions/{id}/')}) == None

        if isQuestion:
            comments = getComments(html, id)
            tags = getTags(html)
            creationTime, editTime, viewCount = getTimeStats(
                html)
            score = getScore(html)
            author, editor, wiki = getQuestionStats(
                html)

            info(
                f"Saving question: id={id} tags={tags} creationTime={creationTime} editTime={editTime} viewCount={viewCount} score={score} wiki={wiki} author={author} editor={editor} comments={comments}")

            cursor_target.execute(
                """
                INSERT INTO questions (id, tags, creationtime, edittime, viewcount, score, wiki, author, editor, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [id, tags, creationTime, editTime, viewCount, score, wiki, author, editor, comments])
            db_target.commit()

        elif html.find("div", {"id": f"answer-{id}"}):  # Ignore offline
            comments = getComments(html, id)
            creationTime, editTime, accepted, score, wiki, author, editor = getAnswerStats(
                html, id)
            questionID = getQuestionID(html)

            info(
                f"Saving answer: id={id} questionID={questionID} accepted={accepted} creationTime={creationTime} editTime={editTime} score={score} wiki={wiki} author={author} editor={editor} comments={comments}")

            cursor_target.execute(
                """
                INSERT INTO answers (id, questionID, accepted, creationtime, edittime, score, wiki, author, editor, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [id, questionID, accepted, creationTime, editTime, score, wiki, author, editor, comments])
            db_target.commit()


if __name__ == "__main__":

    # Connect to the databases
    db_source = connect("rawdata.db")
    cursor_source = db_source.cursor()
    db_target = connect("stackoverflow.db")
    cursor_target = db_target.cursor()
    none_counter = 0

    createTables()

    # Get last processed
    id = cursor_target.execute("""
        SELECT MAX(
            MAX(coalesce(questions.id, 0)),
            MAX(coalesce(answers.id, 0))
            ) AS MaxID
        FROM questions, answers
        """).fetchone()[0] or 0

    # Process
    while True:
        id += 1
        info(f"Processing: {id}")
        if (id % 1 == 0):
            print(f"Processing: {id}")

        data = cursor_source.execute("""
        SELECT html.html FROM html, soitems
        WHERE soitems.id = ?
        AND soitems.htmlID = html.id
        """, [id]).fetchone()
        if data is None:
            print("None:", none_counter)
            none_counter += 1
            if none_counter >= 10:
                raise Exception(
                    "The database returned no entries for 10 consecutive times."
                    "This is probably due to the end of the database.")
            continue
            
        none_counter = 0
        parseItem(id, data[0])
