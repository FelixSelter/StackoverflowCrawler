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

    print(edges)

    fig = plt.figure(1, figsize=(50, 50), dpi=100)
    pos = nx.spring_layout(g, k=2, iterations=50)
    nx.draw(g, with_labels=True, node_size=[amount * 500 for amount in tag_counter.values()],
            pos=pos)  # width=list(nx.get_edge_attributes(g, 'weight').values()),

    plt.savefig('graph.png', dpi=100)


analyse1()
