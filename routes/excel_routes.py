from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from datasources.github_handler import parse_github_event
from database.mongo_client import get_collection




excel_bp = Blueprint("excel_bp", __name__)


@excel_bp.route("/excel/github", methods=["POST"])
def excel_webhook():
    data = request.get_json(force=True)  # parse JSON
    
    print(data)

    # mongo_db.members.insert_one(data)

    return jsonify({"status": "OK"})