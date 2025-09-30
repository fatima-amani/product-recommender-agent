from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()

client = None
database = os.getenv("MONGO_DATABASE")

def get_mongo_client():
    global client
    try:
        if client is None:
            uri = os.getenv("MONGO_URL")
            client = MongoClient(uri)
            client.admin.command("ping")
            print("\nSuccessfully connected to mongo DB")
        return client
    except Exception as e:
        print(f"Error connecting to mongo: {e}")

def get_mongo_db():
    global client
    try:
        client = get_mongo_client()
        return client[database]
    except Exception as e:
        print(f"Error connecting to mongo: {e}")
        
def close_mongo_client():
    client.close()
