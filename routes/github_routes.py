# routes/github_routes.py

import logging
from flask import Blueprint, request, jsonify
from datasources.github_handler import parse_github_event
from database.mongo_client import get_collection
from utils.verify_signature_github import verify_github_signature
from config.settings import GITHUB_SIGNATURE_KEY
from utils.API_event_publisher import notify_eval_push

logger = logging.getLogger(__name__) 

github_bp = Blueprint("github_bp", __name__)

@github_bp.route("/webhook/github", methods=["POST"])
def github_webhook():
    
    logger.info("Received Github webhook request.")
    
    #SIGNATURE VERIFICATION, MUST HAVE THE SAME KEY HERE AS THE ONE DEFIEND IN WEBHOOK IN GITHUB
    secret=GITHUB_SIGNATURE_KEY.encode() #Get signature key from settings.py
    if not verify_github_signature(request, secret):
        logger.warning("Invalid Github webhook signature.")
        return jsonify({"error": "Invalid Signature"}), 403  
    
    
    raw_json = request.get_json()
    if not raw_json:
        logger.warning("Github webhook called without JSON payload.")
        return {"error": "No JSON received"}, 400
    
    # We read the event name from the GitHub header, not in the JSON
    event_name = request.headers.get("X-GitHub-Event")
    raw_json["X-GitHub-Event"] = event_name  # put it in the JSON so parse function sees it

    logger.info("Github webhook request processed successfully.")
    parsed_data = parse_github_event(raw_json)
    
    print(parsed_data)
    if "error" in parsed_data:
        return parsed_data, 400



    team_name = parsed_data["team_name"]
    event_label = parsed_data["event"] #This is either "commit" or "issue"   
    author_login = parsed_data["sender_info"]["login"] #username of the author of the commit or issue
    
    if event_label == "commit":
        collection_name = f"{team_name}_commits"
    elif event_label == "issue":
        collection_name = f"{team_name}_issues"
    
    coll = get_collection(collection_name)




    #COMMUNICATION WITH LD_EVAL USING API
    
    
    logger.info(f"Notifying LD_EVAL about event: {event_name} for team: {team_name}")
    try:
        notify_eval_push(event_name, team_name, author_login)
    except Exception as e:
        logger.error(f"Error notifying LD_EVAL: {e}")
        return {"status": "error", "message": str(e)}, 500
    
    

    
    # If it's a commit push, we may have multiple commits
    if "commits" in parsed_data:
        for commit_doc in parsed_data["commits"]:
            # add top-level fields to each commit if you want
            commit_doc["team_name"] = parsed_data["team_name"]
            commit_doc["sender_info"] = parsed_data["sender_info"]
            commit_doc["event"] = parsed_data["event"]
            commit_doc["repo_name"] = parsed_data["repo_name"]

            logger.info(f"Inserting commit document: {commit_doc}")
            coll.insert_one(commit_doc)

        return {"status": "ok", "message": "Commits inserted"}, 200

    # If it's an issue event
    if "issue" in parsed_data:
        coll.insert_one(parsed_data)
        return {"status": "ok", "message": "Issue inserted"}, 200

    #If its neither a commit or a issue
    coll.insert_one(parsed_data)
    return {"status": "ok", "message": "Stored event doc"}, 200
