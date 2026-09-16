import re


def extract_entities(text: str) -> dict:

    text = text.lower().strip()

    entities = {
        "location": None,
        "issue": None,
        "assignee": None,
        "status": None
    }

    # --------------------------------
    # Extract assignee first
    # --------------------------------

    assign_match = re.search(
        r"\b(?:assign(?:ed)?\s+(?:it\s+)?to)\s+"
        r"(?:the\s+)?(.+?)$",
        text
    )

    if assign_match:
        entities["assignee"] = assign_match.group(1).strip()


    # --------------------------------
    # Extract assignee from search
    # --------------------------------

    search_assignee_match = re.search(
        r"\b(?:assigned\s+to|for)\s+"
        r"(?:the\s+)?(.+?)$",
        text
    )

    if search_assignee_match and (
        "find" in text
        or "search" in text
        or "show" in text
        or "list" in text
    ):

        possible_assignee = search_assignee_match.group(1).strip()

        # Words that usually indicate a person/team/contractor
        assignee_words = [
            "contractor",
            "supervisor",
            "worker",
            "team",
            "manager",
            "electrician",
            "plumber",
            "carpenter",
            "painter",
            "flooring",
            "plumbing",
            "electrical"
        ]

        if any(
            word in possible_assignee
            for word in assignee_words
        ):
            entities["assignee"] = possible_assignee


    # --------------------------------
    # Extract location
    # --------------------------------

    location_match = re.search(
        r"\b(?:in|at|for)\s+(?:the\s+)?(.+?)"
        r"(?=\s+(?:and|assign|assigned|with|status|to|as)\b|$)",
        text
    )

    if location_match:
        possible_location = location_match.group(1).strip()

        # Don't treat an assignee as a location
        if possible_location != entities["assignee"]:
            entities["location"] = possible_location
        
    # --------------------------------
    # Extract location from update command
    # --------------------------------

    update_location_match = re.search(
        r"\b(?:update|change|edit|modify|close|reopen)\s+"
        r"(?:the\s+)?(.+?)\s+snag\b",
        text
    )

    if update_location_match:
        entities["location"] = update_location_match.group(1).strip()    
        
        
    # --------------------------------
    # Extract location from delete command
    # --------------------------------

    delete_location_match = re.search(
        r"\b(?:delete|remove|erase)\s+"
        r"(?:the\s+)?(.+?)\s+snag\b",
        text
    )

    if delete_location_match:
        entities["location"] = delete_location_match.group(1).strip()

    # --------------------------------
    # Extract issue
    # --------------------------------

    issue_words = [
        "ceiling",
        "wall",
        "floor",
        "door",
        "window",
        "leak",
        "paint",
        "plumbing",
        "electrical"
    ]

    for issue in issue_words:

        if re.search(rf"\b{re.escape(issue)}\b", text):

            entities["issue"] = issue
            break


    ()

    # --------------------------------
    # Extract status
    # --------------------------------

    if re.search(r"\bopen\b", text):

        entities["status"] = "open"

    elif re.search(r"\bclosed\b", text):

        entities["status"] = "closed"

    elif re.search(r"\bin progress\b", text):

        entities["status"] = "in progress"

    return entities

