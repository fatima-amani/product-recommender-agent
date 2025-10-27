from google.adk.agents import Agent

from database.graph.crud import get_graph_schema
from database.mongo.crud import get_mongo_schema
from prompts.agent import get_agent_instruction
from tools.graph_tool import graph_tool
from tools.mongo_tool import mongo_tool

from constants import ROOT_AGENT_MODEL

def create_product_recommender_agent():

    graph_schema = get_graph_schema()
    mongo_schema = get_mongo_schema()
    
    root_agent = Agent(
        name="product_recommender_agent",
        model=ROOT_AGENT_MODEL,
        description=(
            "Agent to recommend products based on user queries. Has access to graph DB and MongoDB querying tools."
        ),
        instruction= get_agent_instruction(graph_schema, mongo_schema),
        tools=[graph_tool, mongo_tool],
    )
    
    return root_agent



# Export for ADK
__all__ = ['agent']