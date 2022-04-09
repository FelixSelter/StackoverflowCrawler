def getTimeStats(html, id, status):
    answer = html.find(
        "div", {"id": f"answer-{id}"})
    if answer is None:
        return None, None, "deleted"

    return None, None, status
