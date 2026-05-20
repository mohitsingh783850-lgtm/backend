from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.talent_portal_db
db = client["connect_sphere_db"]
applications_collection = db["applications"]

def get_collection(name: str):
    return db[name]