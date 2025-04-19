# routes/taiga_routes.py


import logging
from flask import Blueprint, request, jsonify
from datasources.taiga_handler import parse_taiga_event
from database.mongo_client import get_collection
from utils.verify_signature_taiga import verify_taiga_signature
from config.settings import TAIGA_SIGNATURE_KEY
from utils.API_event_publisher import notify_eval_push

logger = logging.getLogger(__name__) 
taiga_bp = Blueprint("taiga_bp", __name__)


@taiga_bp.route("/webhook/taiga", methods=["POST"])
def taiga_webhook():
    
    logger.info("Received Taiga webhook request.")
    
    secret=TAIGA_SIGNATURE_KEY.encode()
    if not verify_taiga_signature(request, secret):
        logger.warning("Invalid Taiga webhook signature.")
        return jsonify({"error": "Invalid Signature"}), 403  
    
    
    raw_payload = request.json
    if not raw_payload:
        logger.warning("Taiga webhook called without JSON payload.")
        return jsonify({"error": "No JSON"}), 400

    
    
    event_type= raw_payload.get("type","")
    action_type= raw_payload.get("action","")
    id = raw_payload.get("data",{}).get("id", "")
    team_name = raw_payload.get("data",{}).get("project", {}).get("name", "")
    

    # Decide which Mongo collection to write to:
    if event_type in ["userstory", "relateduserstory"]:
        collection_name = f"{team_name}_userstories"
    elif event_type == "issue":
        collection_name = f"{team_name}_issues"
    elif event_type == "task":
        collection_name = f"{team_name}_tasks"
    elif event_type == "epic":
        collection_name = f"{team_name}_epics"
    else:
        return jsonify({"status": "ignored", "reason": "unsupported type"}), 200

    coll = get_collection(collection_name)

        #Handle the deletion of a document before we parse the payload, to avoid data errors
    if action_type == "delete":
        logger.info(f"Deleting document from {collection_name}. ID={id}")
        
        if not id:
            return jsonify({"error": "No object ID"}), 400
        coll.delete_one({f"{event_type}_id": id})
        logger.info(f"Document with {event_type}={id} has been deleted.")
        return jsonify({"status": "ok"}), 200
    
    
    
    logger.info("Taiga webhook request processed successfully.")
    parsed = parse_taiga_event(raw_payload)


        

    if event_type in ["userstory", "relateduserstory"]:
        # UP-SERT user stories in the same collection
        user_story_id = parsed.get("userstory_id")
        if not user_story_id:
            return jsonify({"error": "No user story ID"}), 400

        logger.info(f"Upserting user story with ID: {user_story_id}")
        result = coll.update_one(
            {"userstory_id": user_story_id},
            {"$set": parsed},
            upsert=True
        )
        
    elif event_type == "task":
        collection_name = f"{team_name}_tasks"
        coll = get_collection(collection_name)

        task_id = parsed.get("task_id")
        if not task_id:
            return jsonify({"error": "No task ID"}), 400

        logger.info(f"Upserting task with ID: {task_id}")
        # Upsert instead of insert
        result = coll.update_one(
            {"task_id": task_id},
            {"$set": parsed},
            upsert=True
    )
        
    elif event_type == "epic":
        collection_name = f"{team_name}_epics"
        coll = get_collection(collection_name)

        epic_id = parsed.get("epic_id")
        if not epic_id:
            return jsonify({"error": "No epic ID"}), 400

        logger.info(f"Upserting epic with ID: {epic_id}")
        # Upsert instead of insert
        result = coll.update_one(
            {"epic_id": epic_id},
            {"$set": parsed},
            upsert=True
    )
        
        
    elif event_type == "issue":
        collection_name = f"{team_name}_issues"
        coll = get_collection(collection_name)

        issue_id = parsed.get("issue_id")
        if not issue_id:
            return jsonify({"error": "No issue ID"}), 400

        logger.info(f"Upserting issue with ID: {issue_id}")
        # Upsert instead of insert
        result = coll.update_one(
            {"issue_id": issue_id},
            {"$set": parsed},
            upsert=True
    )

    else:
        # For issues, tasks, etc. you can do a normal insert (or upsert if you prefer).
        inserted_id = coll.insert_one(parsed).inserted_id


        #COMMUNICATION WITH LD_EVAL USING API
    
    logger.info(f"Notifying LD_EVAL about event: {event_type} for team: {team_name}")
    try:
        notify_eval_push(event_type, team_name)
    except Exception as e:
        logger.error(f"Error notifying LD_EVAL: {e}")
        return jsonify({"error": "Failed to notify LD_EVAL"}), 500
    
    
    return jsonify({"status": "ok"}), 200
