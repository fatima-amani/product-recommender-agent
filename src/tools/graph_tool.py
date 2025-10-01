from langchain_neo4j import GraphCypherQAChain
from langchain_google_genai import ChatGoogleGenerativeAI

from database.graph.db import get_graph_db
from utils.prompts.graph import get_function_response_system

from constants import NEO4J_TOOL_MODEL, NEO4J_TOOL_TEMPERATURE

def neo4j_tool(user_query: str) -> dict:
    """
    Query product graph database using natural language. Returns raw JSON data.
    
    Translates questions like 'find products by brand' into Cypher queries and 
    returns direct database results without additional processing.
    
    Args:
        user_query: Natural language question about products, brands, categories, etc.
    
    Returns:
        Raw JSON results from graph database query execution.
    
    Example: neo4j_tool('Show luxury brands') -> [{'brand': 'Prada'}, ...]
    """
    graph = get_graph_db()
    chain = GraphCypherQAChain.from_llm(
        ChatGoogleGenerativeAI(
            model=NEO4J_TOOL_MODEL, 
            temperature=NEO4J_TOOL_TEMPERATURE
        ), 
        graph=graph,
        verbose=True,
        allow_dangerous_requests=True,
        return_direct=True, 
        function_response_system=f"{get_function_response_system()} \n{graph.schema}"
    )
    
    response = chain.invoke({"query": user_query})
    return response

