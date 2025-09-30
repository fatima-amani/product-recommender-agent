from langchain_mongodb.agent_toolkit.database import MongoDBDatabase
from langchain_mongodb.agent_toolkit.toolkit import InfoMongoDBDatabaseTool

import os
from dotenv import load_dotenv

from .db import get_mongo_client, get_mongo_db

load_dotenv()

def get_mongo_schema():
    db = MongoDBDatabase(
        client=get_mongo_client(),
        database=os.getenv("MONGO_DATABASE")
    )
    schema_tool = InfoMongoDBDatabaseTool(
        db=db
    )

    collection_names = get_mongo_db().list_collection_names()
    schema = ""
    for collection in collection_names:
        schema += str(schema_tool._run(collection_names=collection))
    return schema