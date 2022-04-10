def getStatus(rr):
    """Will check if the id was deleted by the moderators so theres a 404 status

    Args:
        rr (request): The redirected request object

    Returns:
        _type_: _description_
    """

    return "removed" if rr.status_code == 404 else "online"


def getType(r, id):
    """Will check if the id belongs to an answer or a question

    Args:
        r (request): request object containing redirection header

    Returns:
        string: Eather "question" or "answer" depending on the id
    """

    return "question" if r.headers['Location'].startswith(
        f"/questions/{id}") else "answer"


def getComments(html, id):
    """Returns the number of comments for a question or answer

    Args:
        html (bs4 document): The Beautiful Soup 4 document of the question page.
        id (int): The if of eather question or answer that should be parsed.

    Returns:
        int: The amount of comments
    """

    comments_list = html.find("div", {"id": f"comments-{id}"}
                              ).find("ul", {"class": "comments-list"})
    displayed = len(comments_list.find_all("li"))
    hidden = int(comments_list["data-remaining-comments-count"])
    return displayed+hidden
