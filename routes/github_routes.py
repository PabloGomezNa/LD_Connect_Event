# routes/github_routes.py

from flask import Blueprint, request, jsonify
from datasources.github_handler import parse_github_event
from database.mongo_client import get_collection


github_bp = Blueprint("github_bp", __name__)


@github_bp.route("/webhook/github", methods=["POST"])
def github_webhook():
    raw_json = request.get_json()
    if not raw_json:
        return {"error": "No JSON received"}, 400
    
    # We read the event name from the GitHub header, not in the JSON
    event_name = request.headers.get("X-GitHub-Event")
    raw_json["X-GitHub-Event"] = event_name  # put it in the JSON so parse function sees it

    parsed_data = parse_github_event(raw_json)
    if "error" in parsed_data:
        return parsed_data, 400


    team = parsed_data["team_name"]
    event_label = parsed_data["event"]   
    collection_name = f"{team}_{event_label}"
    coll = get_collection(collection_name)

    # If it's a commit push, we may have multiple commits
    if "commits" in parsed_data:
        for commit_doc in parsed_data["commits"]:
            # add top-level fields to each commit if you want
            commit_doc["team_name"] = parsed_data["team_name"]
            commit_doc["sender_info"] = parsed_data["sender_info"]
            commit_doc["event"] = parsed_data["event"]
            commit_doc["repo_name"] = parsed_data["repo_name"]

            coll.insert_one(commit_doc)

        return {"status": "ok", "message": "Commits inserted"}, 200

    # If it's an issue event
    if "issue" in parsed_data:
        coll.insert_one(parsed_data)
        return {"status": "ok", "message": "Issue inserted"}, 200

    coll.insert_one(parsed_data)
    return {"status": "ok", "message": "Stored event doc"}, 200
