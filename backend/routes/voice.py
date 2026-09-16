from fastapi import APIRouter, UploadFile, File

from services.speech_service import speech_to_text
from services.intent_service import detect_intent
from services.entity_service import extract_entities
from services.command_service import execute_command

from utils.confirmation import (
    needs_confirmation,
    create_confirmation_message,
    is_confirmation,
    is_rejection,
    set_pending_command,
    get_pending_command,
    clear_pending_command,
    set_last_command,
    get_last_command,
    set_pending_delete_matches,
    get_pending_delete_matches,
    clear_pending_delete_matches
)


router = APIRouter()


# --------------------------------
# Find a specific delete match
# --------------------------------

def find_delete_match(text, matches):

    text = text.lower().strip()

    for match in matches:

        location = (match.get("location") or "").lower()
        issue = (match.get("issue") or "").lower()
        assignee = (match.get("assignee") or "").lower()

        if location and location in text:
            return match

        if issue and issue in text:
            return match

        if assignee and assignee in text:
            return match

    return None


# --------------------------------
# Voice endpoint
# --------------------------------

@router.post("/voice")
async def process_voice(file: UploadFile = File(...)):

    # --------------------------------
    # Read audio
    # --------------------------------

    audio_bytes = await file.read()

    if not audio_bytes:

        return {
            "success": False,
            "message": "Audio file is empty"
        }


    # --------------------------------
    # Speech -> Text
    # --------------------------------

    text = speech_to_text(audio_bytes)

    print("RECOGNIZED TEXT:", repr(text))


    # --------------------------------
    # Handle pending delete clarification
    # --------------------------------

    pending_matches = get_pending_delete_matches()

    if pending_matches:

        selected_match = find_delete_match(
            text,
            pending_matches
        )

        # --------------------------------
        # User identified a specific snag
        # --------------------------------

        if selected_match:

            entities = {
                "location": selected_match.get("location"),
                "issue": selected_match.get("issue"),
                "assignee": selected_match.get("assignee"),
                "status": selected_match.get("status"),
                "_id": selected_match.get("id")
            }

            set_pending_command(
                "delete",
                entities
            )

            clear_pending_delete_matches()

            location = entities.get("location") or "that location"
            issue = entities.get("issue") or "that"

            return {
                "success": True,
                "text": text,
                "intent": "delete",
                "entities": entities,
                "confirmation_required": True,
                "confirmation_message": (
                    f"I found the {issue} snag at {location}. "
                    "Are you sure you want to delete it?"
                )
            }


        # --------------------------------
        # User did not identify a snag
        # --------------------------------

        return {
            "success": True,
            "text": text,
            "intent": "delete",
            "entities": {},
            "confirmation_required": False,
            "command": {
                "success": False,
                "message": (
                    "I still need more information. "
                    "Please mention the location, issue, or assignee."
                )
            }
        }


    # --------------------------------
    # Check confirmation
    # --------------------------------

    print("CONFIRMATION TEST TEXT:", repr(text))

    if is_confirmation(text):

        pending_intent, pending_entities = get_pending_command()

        if pending_intent:

            command_result = execute_command(
                pending_intent,
                pending_entities
            )

            # Save the successful command as the last command
            if command_result.get("success"):

                set_last_command(
                    pending_intent,
                    pending_entities
                )

            clear_pending_command()

            return {
                "success": True,
                "text": text,
                "intent": pending_intent,
                "entities": pending_entities,
                "confirmation_required": False,
                "command": command_result
            }


    # --------------------------------
    # Check rejection
    # --------------------------------

    if is_rejection(text):

        pending_intent, pending_entities = get_pending_command()

        if pending_intent:

            clear_pending_command()

            return {
                "success": True,
                "text": text,
                "intent": pending_intent,
                "entities": pending_entities,
                "confirmation_required": False,
                "command": {
                    "success": False,
                    "message": "Action cancelled."
                }
            }


    # --------------------------------
    # Text -> Intent
    # --------------------------------

    intent = detect_intent(text)


    # --------------------------------
    # Text -> Entities
    # --------------------------------

    entities = extract_entities(text)


    # --------------------------------
    # Handle follow-up update commands
    # --------------------------------

    if intent == "update":

        last_intent, last_entities = get_last_command()

        if last_intent == "update" and last_entities:

            for key in ["location", "issue", "status"]:

                if not entities.get(key):

                    entities[key] = last_entities.get(key)


            # Keep the previous location if the user says
            # something like "assign it to the contractor"


            if not entities.get("location"):

                entities["location"] = last_entities.get(
                    "location"
                )


            if not entities.get("issue"):

                entities["issue"] = last_entities.get(
                    "issue"
                )


    # --------------------------------
    # Check whether confirmation is required
    # --------------------------------

    if needs_confirmation(intent):

        set_pending_command(
            intent,
            entities
        )

        confirmation_message = create_confirmation_message(
            intent,
            entities
        )

        return {
            "success": True,
            "text": text,
            "intent": intent,
            "entities": entities,
            "confirmation_required": True,
            "confirmation_message": confirmation_message
        }


    # --------------------------------
    # Execute command
    # --------------------------------

    command_result = execute_command(
        intent,
        entities
    )


    # --------------------------------
    # Store multiple delete matches
    # --------------------------------

    if (
        intent == "delete"
        and command_result.get("matches")
    ):

        set_pending_delete_matches(
            command_result["matches"]
        )


    # --------------------------------
    # Return response
    # --------------------------------

    return {
        "success": True,
        "text": text,
        "intent": intent,
        "entities": entities,
        "command": command_result
    }