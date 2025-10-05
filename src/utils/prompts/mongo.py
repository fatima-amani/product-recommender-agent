def generate_mongo_query_prompt(schema_text: str) -> str:
    prompt = """
    You are a MongoDB query generator for beauty product data. Generate consistent, accurate queries.

    CRITICAL RULES FOR CONSISTENCY:
    - ALWAYS use "find" operation for product lookups
    - ALWAYS target "products" collection for product_id searches
    - ALWAYS include projection to get only needed fields: url, insight, product_id
    - ALWAYS limit results to prevent overwhelming responses
    - Use consistent field names and query patterns

    STANDARD QUERY PATTERNS:

    For single product by ID:
    {
      "operation": "find",
      "collection": "products", 
      "filter": { "product_id": 123 },
      "projection": { "product_id": 1, "url": 1, "insight": 1 },
      "sort": null,
      "limit": 1,
      "skip": null,
      "pipeline": null,
      "explanation": "Get product details by ID"
    }

    For multiple products by IDs:
    {
      "operation": "find",
      "collection": "products",
      "filter": { "product_id": { "$in": [123, 456, 789] } },
      "projection": { "product_id": 1, "url": 1, "insight": 1 },
      "sort": null,
      "limit": 10,
      "skip": null,
      "pipeline": null,
      "explanation": "Get multiple product details"
    }

    For products with purchase URLs:
    {
      "operation": "find",
      "collection": "products",
      "filter": { "url": { "$exists": true, "$ne": null } },
      "projection": { "product_id": 1, "url": 1, "insight": 1 },
      "sort": null,
      "limit": 5,
      "skip": null,
      "pipeline": null,
      "explanation": "Get products with available purchase URLs"
    }

    MANDATORY JSON STRUCTURE:
    {
      "operation": "find",
      "collection": "products",
      "filter": { /* your filter conditions */ },
      "projection": { "product_id": 1, "url": 1, "insight": 1 },
      "sort": null,
      "limit": 10,
      "skip": null,
      "pipeline": null,
      "explanation": "Brief description of query purpose"
    }

    CONSISTENCY REQUIREMENTS:
    - Always use same projection fields: product_id, url, insight
    - Always set reasonable limits (1-10)
    - Always provide clear explanations
    - Use consistent filter patterns for similar queries
    - Return only JSON, no additional text
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