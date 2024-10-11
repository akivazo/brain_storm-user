from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pydantic import BaseModel, Field, ValidationError
from typing import Type, List

class User(BaseModel):
    name: str
    password: str
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
    # validate that the accepted json is containing all the data nedded
    instance = None
    try:
        instance = cls(**json)
    except ValidationError as e:
        return None, e.json()
    return instance.__dict__, ""

@server.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    instance, error_message = validate_json_schema(data, User)
    if not instance:
        return jsonify({"error": error_message}), 400
    
    # check if exist
    name = instance["name"]
    result = user_collection.find_one({"name": name})
    if result:
        return jsonify({"error": f"User with name {name} is already exist"}), 409
    user_collection.insert_one(instance)
    return jsonify("User Created Succesfully"), 201

@server.route("/user/<name>/<password>", methods=["GET"])
def get_user(name, password):
    user = user_collection.find_one({"name": name, "password": password}, {"_id": 0})
    if user:
        return jsonify({"user": user})
    return jsonify({"error": f"User with id '{name}' and the given password was not found"}), 404


@server.route("/user/<name>/<password>", methods=["DELETE"])
def delete_idea(name, password):
    result = user_collection.delete_one({"name": name, "password": password})
    assert result.deleted_count <= 1
    if result.deleted_count == 1:
        return jsonify(f"User with name '{name}' was deleted successfully"), 204
    if result.deleted_count == 0:
        return jsonify({"error": "Can't find user"}), 404

if __name__ == "__main__":
    import os, dotenv
    dotenv.load_dotenv()
    mongo_client = MongoClient(os.environ["USER_MONGODB_URI"])
    set_mongo_client(mongo_client)
    server.run(debug=True, port=5000)
    mongo_client.close()