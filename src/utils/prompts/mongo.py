def generate_mongo_query_prompt(schema_text: str) -> str:
    prompt = """
    You are an expert MongoDB assistant.

    Your task:
    - Generate valid MongoDB queries in **JSON format** based on natural language instructions.
    - Use the provided database schema to understand collection names and field types.
    - Only generate queries that are syntactically correct.
    - If the user's request cannot be satisfied, explain why instead of guessing.

    CRITICAL INSTRUCTIONS:
    1. Always return a JSON object, not a string.
    2. Include the following fields in the JSON:
       - operation: the MongoDB operation ("find", "aggregate", "insert", "update", etc.)
       - collection: the target collection name
       - filter: the query filter object (default: {})
       - projection: fields to include/exclude (default: null)
       - sort: sorting object (default: null)
       - limit: integer limit (default: null)
       - skip: integer skip (default: null)
       - pipeline: for aggregation queries, an array of pipeline stages (default: null)
       - explanation: short explanation of what the query does
    3. Use proper MongoDB operators: $eq, $gt, $gte, $lt, $lte, $in, $ne, $and, $or, etc.
    4. Do not include any natural language text, only the JSON object.

    VALID EXAMPLES:
    - "find products with id 1" →
      {
        "operation": "find",
        "collection": "products",
        "filter": { "product_id": 1 },
        "projection": null,
        "sort": null,
        "limit": null,
        "skip": null,
        "pipeline": null,
        "explanation": "Find products with id 1"
      }

    - "latest 10 orders" →
      {
        "operation": "find",
        "collection": "orders",
        "filter": {},
        "projection": null,
        "sort": { "order_date": -1 },
        "limit": 10,
        "skip": null,
        "pipeline": null,
        "explanation": "Get latest 10 orders sorted by order_date"
      }
    """
    return prompt + f"\n\nDatabase schema:\n{schema_text}"


def get_query_checker_prompt(schema_text ) -> str:
    prompt =  """
You are a MongoDB query validator.

Your task:
1. Validate MongoDB queries against the provided database schema.
2. Ensure queries are syntactically correct and structured as a JSON object matching the MongoQueryModel:
   - operation: "find" or "aggregate" (only read operations are allowed)
   - collection: target collection name
   - filter: dict for query conditions (default empty dict)
   - projection: dict for included/excluded fields (optional)
   - sort: dict for sorting (optional)
   - limit: integer (optional)
   - skip: integer (optional)
   - pipeline: list of aggregation stages (optional)
   - explanation: short text explaining the query (optional)
3. If there are syntax errors (missing braces, invalid operators, etc.) or the operation is not allowed (write operations), mark the query as invalid.
4. Return a JSON object with the following fields:
   - is_valid: true/false
   - issues: list of issues found (empty if valid)
    """
    format = f"""
    Database schema:
    {schema_text}
    """

    return prompt+format