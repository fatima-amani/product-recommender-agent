from langchain_neo4j import Neo4jGraph

import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("URI")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

global graph
graph = None

def get_graph_db():
    global graph
    if graph is None:
        graph = Neo4jGraph(
            url=URI, 
            username=USER, 
            password=PASSWORD,
            database=DATABASE,
            enhanced_schema=True
        )
    return graph