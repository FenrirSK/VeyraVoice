pending_command = {
    "intent": None,
    "entities": None
}

pending_delete_matches = []

last_command ={
    "intent": None,
    "entities": None
}

def needs_confirmation(intent: str) -> bool:
    """
    Check whether an intent needs user confirmation
    before executing the command.
    """
    
    confirmation_required = [
        "create_snag",
        "update",
        "delete"
    ]
    
    return intent in confirmation_required

def create_confirmation_message(intent: str, entities: dict) -> str:
    """
    Create a message  asking the user to confirm an action.
    """
    
    if intent == "create_snag":
        
        location = entities.get("location") or "unknown location"
        issue = entities.get("issue") or "unknown issue"
        assignee = entities.get("assignee") or "unassigned"
        
        return (
            f"I found a snag for {issue} at {location},"
            f"assigned to {assignee}, "
            f"Should i create it?"
        )
        
    if intent == "delete":
        return "Are you sure you want to delete this?"
    
    if intent == "update":
        return "Are you sure you want to update this?"
    
    return "Do you want me to continue?"

def is_confirmation(text: str) -> bool:
    """
    Check whether the user confirmed the action.
    """
    
    confirmation_words = [
        "yes",
        "yeah",
        "yep",
        "sure",
        "okay",
        "ok",
        "confirm",
        "do it",
        "ya"
    ]
    
    text = text.lower().strip()
    
    return any(word in text for word in confirmation_words)

def is_rejection(text: str):
    """
    Check whether the user rejected the action. 
    """
    
    rejection_words = [
        "no",
        "nope",
        "cancel",
        "don't",
        "do not"
    ]
    
    text = text.lower().strip()
    
    return any(word in  text for word in rejection_words)


def set_pending_command(intent: str, entities: dict):
    """
    store the command waiting for confirmation.
    """
    
    pending_command["intent"] = intent
    pending_command["entities"] = entities
    
def get_pending_command():
    """
    get the command waiting for confirmation.
    """
    
    return pending_command["intent"], pending_command["entities"]

def clear_pending_command():
    """
    clear the pending command after confirmation or rejection.
    """
    
    pending_command["intent"] = None
    pending_command["entities"] = None
    
def set_last_command(intent: str, entities: dict):

    last_command["intent"] = intent
    last_command["entities"] = entities.copy()


def get_last_command():

    return (
        last_command["intent"],
        last_command["entities"]
    )


def clear_last_command():

    last_command["intent"] = None
    last_command["entities"] = None
    
def set_pending_delete_matches(matches):

    global pending_delete_matches

    pending_delete_matches = matches


def get_pending_delete_matches():

    return pending_delete_matches


def clear_pending_delete_matches():

    global pending_delete_matches

    pending_delete_matches = []