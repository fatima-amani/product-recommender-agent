from database.mongo.db import get_mongo_db
from database.mongo.crud import get_mongo_schema
from models.mongo import MongoQueryModel, QueryValidationResult
from utils.prompts.mongo import generate_mongo_query_prompt, get_query_checker_prompt
from utils.llm_utils import run_llm, serialize

from constants import MONGO_TOOL_MODEL, MONGO_TOOL_TEMPERATURE


def generate_mongo_query(user_query):
    schema_text = get_mongo_schema()

    result = run_llm(
        llm_model=MONGO_TOOL_MODEL,
        temperature=MONGO_TOOL_TEMPERATURE,
        pydantic_model=MongoQueryModel,
        system_msg=generate_mongo_query_prompt(schema_text),
        human_msg=user_query,
    )
    
    return result

def validate_mongo_query(query):
    schema_text = get_mongo_schema()

    result = run_llm(
        llm_model=MONGO_TOOL_MODEL,
        temperature=MONGO_TOOL_TEMPERATURE,
        pydantic_model=QueryValidationResult,
        system_msg=get_query_checker_prompt(schema_text),
        human_msg=f"Validate this: {query}"        
    )

    return result.is_valid

def run_query(model: MongoQueryModel):
    db = get_mongo_db()
    col = db[model.collection]

    if model.operation == "find":
        cursor = col.find(model.filter, model.projection or {})
        if model.sort:
            cursor = cursor.sort(list(model.sort.items()))
        if model.skip:
            cursor = cursor.skip(model.skip)
        if model.limit:
            cursor = cursor.limit(model.limit)
        return [serialize(d) for d in cursor]

    elif model.operation == "aggregate":
        return [serialize(d) for d in col.aggregate(model.pipeline or [])]


    else:
        raise ValueError(f"Unsupported operation: {model.operation}")


def mongo_tool(user_query: str) -> list:
    """
    Query MongoDB with natural language. Returns raw JSON results.
    
    Args:
        user_query: Question about products, reviews, users, etc.
    
    Returns:
        list: Raw JSON data from the MongoDB query.
    """
    try:
        print(f"\nMongo_tool received query: {user_query}")
        query = generate_mongo_query(user_query)
        is_valid = validate_mongo_query(query)
        if is_valid:
            result = run_query(query)
            print(f"Mongo Tool Result: {result}\n")
            return result if result else [{"message": "No results found for the given query"}]
        else:
            return [{"error": "Invalid MongoDB query generated", "query": str(query)}]
    except Exception as e:
        return [{"error": f"Database query failed: {str(e)}"}]
