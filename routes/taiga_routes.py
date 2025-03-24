# routes/taiga_routes.py

'''
TODO:

- Add Guicorn to better flask
- Add a logger
- Add authentication for more security

- If we delete an epic/issue/task/userstory, we should delete it from the database?


'''
from flask import Blueprint, request, jsonify
from datasources.taiga_handler import parse_taiga_event
from database.mongo_client import get_collection

taiga_bp = Blueprint("taiga_bp", __name__)

@taiga_bp.route("/webhook/taiga", methods=["POST"])
def taiga_webhook():
    raw_payload = request.json
    if not raw_payload:
        return jsonify({"error": "No JSON"}), 400

    parsed = parse_taiga_event(raw_payload)
    event_type = parsed.get("event_type", "")
    team_name = parsed.get("team_name","")

    # Decide which Mongo collection to write to:
    if event_type in ["userstory", "relateduserstory"]:
        collection_name = f"{team_name}_taiga_userstories"
    elif event_type == "issue":
        collection_name = f"{team_name}_taiga_issues"
    elif event_type == "task":
        collection_name = f"{team_name}_taiga_tasks"
    elif event_type == "epic":
        collection_name = f"{team_name}_taiga_epic"
    else:
        return jsonify({"status": "ignored", "reason": "unsupported type"}), 200

    coll = get_collection(collection_name)

    if event_type in ["userstory", "relateduserstory"]:
        # UP-SERT user stories in the same collection
        user_story_id = parsed.get("id")
        if not user_story_id:
            return jsonify({"error": "No user story ID"}), 400

        result = coll.update_one(
            {"id": user_story_id},
            {"$set": parsed},
            upsert=True
        )
        
    elif event_type == "task":
        collection_name = f"{team_name}_taiga_tasks"
        coll = get_collection(collection_name)

        task_id = parsed.get("task_id")
        if not task_id:
            return jsonify({"error": "No task ID"}), 400

        # Upsert instead of insert
        result = coll.update_one(
            {"task_id": task_id},
            {"$set": parsed},
            upsert=True
    )
        
    elif event_type == "epic":
        collection_name = f"{team_name}_taiga_epic"
        coll = get_collection(collection_name)

        epic_id = parsed.get("epic_id")
        if not epic_id:
            return jsonify({"error": "No epic ID"}), 400

        # Upsert instead of insert
        result = coll.update_one(
            {"epic_id": epic_id},
            {"$set": parsed},
            upsert=True
    )
        
        
    elif event_type == "issue":
        collection_name = f"{team_name}_taiga_issues"
        coll = get_collection(collection_name)

        issue_id = parsed.get("issue_id")
        if not issue_id:
            return jsonify({"error": "No issue ID"}), 400

        # Upsert instead of insert
        result = coll.update_one(
            {"issue_id": issue_id},
            {"$set": parsed},
            upsert=True
    )

    else:
        # For issues, tasks, etc. you can do a normal insert (or upsert if you prefer).
        inserted_id = coll.insert_one(parsed).inserted_id

    return jsonify({"status": "ok"}), 200
