import os 
from dotenv import load_dotenv
from pymongo import MongoClient
from pathlib import Path

load_dotenv(Path(__file__).with_name(".env"))

load_dotenv()
client = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000)
runs = client["runs_coach"]["runs"]

