from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from uuid import uuid4
from pydantic import BaseModel, Field, ValidationError
from typing import Type, List

class User(BaseModel):
    id: str
    name: str
    email: str
    tags: List[str] = Field(default_factory=list)


server = Flask(__name__)
CORS(server)
user_collection = None

def set_mongo_client(mongo_client: MongoClient):
    global user_collection
    user_collection = mongo_client.get_database("brain_storm").get_collection("user")

@server.route("/")
def root():
    return "User Api"

def validate_json_schema(json: dict, cls: Type):
    # validate that the accepted json is cintaining all the data nedded
    instance = None
    try:
        instance = cls(**json)
    except ValidationError as e:
        return None, e.json()
    return instance.__dict__, ""

@server.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    id = str(uuid4())
    data["id"] = id
    instance, error_message = validate_json_schema(data, User)
    if not instance:
        return jsonify({"error": error_message}), 400
    
    user_collection.insert_one(instance)
    return jsonify({"id": id}), 201

@server.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = user_collection.find_one({"id": id}, {"_id": 0})
    if user:
        return jsonify({"user": user})
    return jsonify({"error": f"User with id '{id}' was not found"}), 404


@server.route("/user/<id>", methods=["DELETE"])
def delete_idea(id):
    user_collection.delete_one({"id": id})
    return jsonify(f"User with id '{id}' was deleted successfully"), 204


if __name__ == "__main__":
    import os, dotenv
    dotenv.load_dotenv()
    mongo_client = MongoClient(os.environ["USER_MONGODB_URI"])
    set_mongo_client(mongo_client)
    server.run(debug=True, port=5000)
    mongo_client.close()