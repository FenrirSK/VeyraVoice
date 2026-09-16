import re

from database.connection import db


def execute_command(intent: str, entities: dict):

    if intent == "create_snag":
        return create_snag(entities)

    if intent == "search_snags":
        return search_snags(entities)
    
    if intent == "update":
        return update_snag(entities)
    
    if intent == "delete":
        return delete_snag(entities)

    return {
        "success": False,
        "message": "Sorry, I didn't understand that command. Please try again."
    }


def create_snag(entities: dict):

    snag = {
        "location": entities.get("location"),
        "issue": entities.get("issue"),
        "assignee": entities.get("assignee"),
        "status": "open"
    }

    result = db.snags.insert_one(snag)
    

    return {
        "success": True,
        "message": "Snag created successfully",
        "snag_id": str(result.inserted_id),
        "snag": {
            "location": snag["location"],
            "issue": snag["issue"],
            "assignee": snag["assignee"],
            "status": snag["status"]
        }
    }


def search_snags(entities: dict):

    query = {}

    # Search location flexibly
    if entities.get("location"):
        query["location"] = {
            "$regex": re.escape(entities["location"]),
            "$options": "i"
        }

    # Search issue flexibly
    if entities.get("issue"):
        query["issue"] = {
            "$regex": re.escape(entities["issue"]),
            "$options": "i"
        }

    # Search assignee flexibly
    if entities.get("assignee"):
        query["assignee"] = {
            "$regex": re.escape(entities["assignee"]),
            "$options": "i"
        }

    # Status remains an exact match
    if entities.get("status"):
        query["status"] = entities["status"]

    snags = list(db.snags.find(query))

    for snag in snags:
        snag["_id"] = str(snag["_id"])

    return {
        "success": True,
        "count": len(snags),
        "snags": snags
    }
    
def update_snag(entities: dict):

    query = {}

    if entities.get("location"):
        query["location"] = {
            "$regex": re.escape(entities["location"]),
            "$options": "i"
        }

    if entities.get("issue"):
        query["issue"] = {
            "$regex": re.escape(entities["issue"]),
            "$options": "i"
        }

    if not query:
        return {
            "success": False,
            "message": "I need more information to find the snag."
        }

    update_data = {}

    if entities.get("status"):
        update_data["status"] = entities["status"]

    if entities.get("assignee"):
        update_data["assignee"] = entities["assignee"]

    if not update_data:
        return {
            "success": False,
            "message": "I need to know what should be updated."
        }

    result = db.snags.update_one(
        query,
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return {
            "success": False,
            "message": "No matching snag found."
    }

    if result.modified_count == 0:
        return {
            "success": True,
            "message": "Snag already has the requested values.",
            "modified_count": 0
        }

    return {
        "success": True,
        "message": "Snag updated successfully",
        "modified_count": result.modified_count,
        "updated": update_data
    }
    
def delete_snag(entities: dict):

    query = {}

    if entities.get("location"):
        query["location"] = {
            "$regex": re.escape(entities["location"]),
            "$options": "i"
        }

    if entities.get("issue"):
        query["issue"] = {
            "$regex": re.escape(entities["issue"]),
            "$options": "i"
        }

    if not query:
        return {
            "success": False,
            "message": "I need more information to find the snag."
        }

    matching_snags = list(
        db.snags.find(query)
    )

    # No matching snag
    if len(matching_snags) == 0:
        return {
            "success": False,
            "message": "No matching snag found."
        }

    # Multiple matching snags
    if len(matching_snags) > 1:

        matches = []

        for snag in matching_snags:

            matches.append({
                "id": str(snag["_id"]),
                "location": snag.get("location"),
                "issue": snag.get("issue"),
                "assignee": snag.get("assignee"),
                "status": snag.get("status")
            })

        return {
            "success": False,
            "message": (
                f"I found {len(matching_snags)} matching snags. "
                "Please tell me which one you want to delete."
            ),
            "count": len(matching_snags),
            "matches": matches
        }

    # Exactly one matching snag
    result = db.snags.delete_one(query)

    if result.deleted_count == 0:
        return {
            "success": False,
            "message": "The snag could not be deleted."
        }

    return {
        "success": True,
        "message": "Snag deleted successfully."
    }