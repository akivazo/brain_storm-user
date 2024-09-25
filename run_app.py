from app.user_api import server, set_mongo_client
from pymongo import MongoClient
from waitress import serve
import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    mongo_client = MongoClient(os.environ["IDEA_MONGODB_URI"])
    set_mongo_client(mongo_client)
    serve(server, host="0.0.0.0", port=8000)