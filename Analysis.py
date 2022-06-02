import json
from sqlite3 import connect

import matplotlib.pyplot as plt
import networkx as nx

db = connect('stackoverflow.db')
cursor = db.cursor()


def analyse1():
    global cursor
    g = nx.Graph()
    tag_counter = dict()
    tag_combination_counter = dict()

    for result in cursor.execute("""
    SELECT tags from questions
    """):
        tags = json.loads(result[0])
        for tag in tags:
            tag_counter[tag] = 1 if tag not in tag_counter else tag_counter[tag] + 1
            for followingTag in tags[tags.index(tag) + 1:]:
                key = tuple(sorted([tag, followingTag]))
                tag_combination_counter[key] = 1 if key not in tag_combination_counter else tag_combination_counter[
                                                                                                key] + 1

    g.add_nodes_from(tag_counter.keys())

    edges = 0
    for tags, amount in tag_combination_counter.items():
        # jaccard coefficient
        importance = amount / tag_counter[tags[0]] + amount / tag_counter[tags[1]]
        g.add_edge(tags[0], tags[1], weight=importance * 100)
        edges += 1

    fig = plt.figure(1, figsize=(50, 50), dpi=100)
    pos = nx.spring_layout(g, k=2, iterations=50)
    nx.draw(g, with_labels=True, node_size=[amount * 500 for amount in tag_counter.values()],
            pos=pos)  # width=list(nx.get_edge_attributes(g, 'weight').values()),

    plt.savefig('graph.png', dpi=100)


def analyse2():
    global cursor
    cursor.execute("""
        SELECT count(id),
           strftime('%H', creationtime) as hour
        FROM questions
        GROUP BY hour
    """)
    amount, hour = zip(*cursor.fetchall())

    fig = plt.figure()
    fig.suptitle('Questions per daytime', fontsize=20)
    plt.xlabel('Hour', fontsize=16)
    plt.ylabel('Asked Questions', fontsize=16)
    plt.bar(hour, amount)
    plt.savefig('time.png', dpi=100)


def analyse3():
    global cursor
    cursor.execute("""
        SELECT author, Count(*) as contributions
        FROM (SELECT questions.author
              FROM questions
              WHERE wiki = false
              UNION ALL
              SELECT answers.author
              FROM answers
              WHERE wiki = false)
        GROUP BY author
        ORDER BY contributions DESC
        LIMIT 10
    """)
    author, amount = zip(*(cursor.fetchall()))

    fig = plt.figure()
    fig.suptitle('Questions and answers', fontsize=20)
    plt.xticks(rotation=90)
    plt.xlabel('Username', fontsize=16)
    plt.ylabel('Contributions', fontsize=16)
    plt.bar(author, amount)
    plt.tight_layout()
    plt.savefig('contribution.png', dpi=100)


def analyse4():
    global cursor
    cursor.execute("""
        SELECT author, Count(*) as questions
        FROM questions
        WHERE wiki = false
        GROUP BY author
        ORDER BY questions DESC
        LIMIT 10
    """)
    author, amount = zip(*(cursor.fetchall()))

    fig = plt.figure()
    fig.suptitle('Questions', fontsize=20)
    plt.xticks(rotation=90)
    plt.xlabel('Username', fontsize=16)
    plt.ylabel('Questions', fontsize=16)
    plt.bar(author, amount)
    plt.tight_layout()
    plt.savefig('questions.png', dpi=100)


def analyse5():
    global cursor
    cursor.execute("""
        SELECT author, Count(*) as answers
        FROM answers
        WHERE wiki = false
        GROUP BY author
        ORDER BY answers DESC
        LIMIT 10
    """)
    author, amount = zip(*(cursor.fetchall()))

    fig = plt.figure()
    fig.suptitle('Answers', fontsize=20)
    plt.xticks(rotation=90)
    plt.xlabel('Username', fontsize=16)
    plt.ylabel('Answers', fontsize=16)
    plt.bar(author, amount)
    plt.tight_layout()
    plt.savefig('answers.png', dpi=100)


def analyse6():
    global cursor
    cursor.execute("""
        SELECT author, score
        FROM (SELECT questions.author, questions.score
              FROM questions
              UNION ALL
              SELECT answers.author, answers.score
              FROM answers)
        GROUP BY author
        ORDER BY score ASC
        LIMIT 10
    """)
    author, score = zip(*(cursor.fetchall()))

    fig = plt.figure()
    fig.suptitle('Least score', fontsize=20)
    plt.xticks(rotation=90)
    plt.xlabel('Username', fontsize=16)
    plt.ylabel('Score', fontsize=16)
    plt.bar(author, score)
    plt.tight_layout()
    plt.savefig('least score.png', dpi=100)


def analyse7():
    global cursor
    cursor.execute("""
        SELECT author, score
        FROM (SELECT questions.author, questions.score
              FROM questions
              UNION ALL
              SELECT answers.author, answers.score
              FROM answers)
        GROUP BY author
        ORDER BY score DESC
        LIMIT 10
    """)
    author, score = zip(*(cursor.fetchall()))

    fig = plt.figure()
    fig.suptitle('Most score', fontsize=20)
    plt.xticks(rotation=90)
    plt.xlabel('Username', fontsize=16)
    plt.ylabel('Score', fontsize=16)
    plt.bar(author, score)
    plt.tight_layout()
    plt.savefig('most score.png', dpi=100)


def analyse8():
    global cursor
    cursor.execute("""
        SELECT Count(score)
        FROM (SELECT questions.score
              FROM questions
              UNION ALL
              SELECT  answers.score
              FROM answers)
        WHERE score = 0
        GROUP BY score

    """)
    zero = cursor.fetchone()[0]

    cursor.execute("""
            SELECT Count(score)
            FROM (SELECT questions.score
                  FROM questions
                  UNION ALL
                  SELECT  answers.score
                  FROM answers)
            WHERE score < 0
            GROUP BY score

        """)
    less = cursor.fetchone()[0]

    cursor.execute("""
            SELECT Count(score)
            FROM (SELECT questions.score
                  FROM questions
                  UNION ALL
                  SELECT  answers.score
                  FROM answers)
            WHERE score > 0
            GROUP BY score

        """)
    more = cursor.fetchone()[0]

    fig, ax = plt.subplots()
    fig.suptitle('Score less/more/zero', fontsize=20)
    ax.pie([zero, less, more], labels=["Zero", "Negative", "Positive"], autopct='%1.11f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.savefig('score+-.png', dpi=100)


if __name__ == "__main__":
    # analyse8()
    analyse1()
# analyse2()
# analyse3()
# analyse4()
# analyse5()
# analyse6()
# analyse7()
