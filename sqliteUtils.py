import sqlite3
from datetime import datetime


def initDB():
    """Will create the database and the table if it doesnt exist

    Returns:
        sqlite connection: Required to save and close the database,
        sqlite cursor: Required to execute sql statements
    """

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


def insertData(cursor, id: int, type: str, status: str, tags: list[str], creationTime: datetime, editTime: datetime, viewCount: int, accepted: bool, score: int, wiki: bool, author: str, editor: str, answers: int, comments: int):
    """Will insert the data into the database

    Args:
        cursor (sqlite cursor): Required to execute sql statements
        id (int): The id of the question or answer
        type (str): If its a "question" or an "answer"
        status (str): If its "removed", "deleted" or "online"
        tags (list[str]): All tags of a question.
        creationTime (datetime): The time when the question or answer was created
        editTime (datetime): The time when the question or answer was edited
        viewCount (int): How many people have seen the question
        accepted (bool): If the answer was accepted
        score (int): How many votes the question or answer has
        wiki (bool): If the question or answer was archived in the community wiki
        author (str): The name of the person who created the question or answer
        editor (str): The name of the last person who edited the question or answer
        answers (int): How many answers a question has
        comments (int): How many comments the question or answer has
    """

    cursor.execute("""
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
        VALUES     (?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ? );  
                    """,
                   (id,
                    type,
                    status,
                    tags,
                    creationTime,
                    editTime,
                    viewCount,
                    accepted,
                    score,
                    wiki,
                    author,
                    editor,
                    answers,
                    comments))
