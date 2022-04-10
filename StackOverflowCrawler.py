import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

import sqliteUtils
import questionAnswerParser
import questionParser
import answerParser


def requestData(id):
    """Will make 2 get requests to determine if the id belongs to an answer or a question
       and to return the html code of the question page

    Args:
        id (int): The if of eather question or answer that should be requested.

    Returns:
        request: Contains redirection information so the script knows if the id belongs to an answer or a question,
        request: Contains the html response of the question page
    """

    while True:
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

        if r.status_code == 100000:  # Disable this for now
            print("RATELIMIT waiting 5 minutes")
            sleep(5*60)
            continue
        else:
            break

    return r, rr


if __name__ == '__main__':
    RATELIMIT = 50

    db, cursor = sqliteUtils.initDB()
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
        status = questionAnswerParser.getStatus(r, rr)
        type = questionAnswerParser.getType(r, id, status)

        if status == "online":

            if type == "question":
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
                comments = questionAnswerParser.getComments(html, id)

        sqliteUtils.insertData(cursor, id, type, status, tags, creationTime,
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
