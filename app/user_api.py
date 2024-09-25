from flask import Flask, request, jsonify
from pymongo import MongoClient
from uuid import uuid4
server = Flask(__name__)
user_collection = None

def set_mongo_client(mongo_client: MongoClient):
    global user_collection
    user_collection = mongo_client.get_database("brain_storm").get_collection("user")

@server.route("/")
def root():
    return "User Storage"

def validate_idea_data(data):
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing or empty field: {field}"
    return True, ""

@server.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    is_valid, error_message = validate_idea_data(data)
    if not is_valid:
        return jsonify(error_message), 400
    id = str(uuid4())
    user_dict = {"id": id, "name": data['name'], "email": data['email'], "tags":data.get('tags', [])}
    user_collection.insert_one(user_dict)
    return jsonify(id), 200

@server.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = user_collection.find_one({"id": id})
    if user:
        del user["_id"] # mongodb id. we dont need it
        return jsonify(user)
    return jsonify(f"User with id '{id}' was not found"), 404


@server.route("/user/<id>", methods=["DELETE"])
def delete_idea(id):
    user_collection.delete_one({"id": id})
    return jsonify(f"User with id '{id}' was deleted successfully"), 204