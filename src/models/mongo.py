from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MongoQueryModel(BaseModel):
    operation: str
    collection: str
    filter: Dict[str, Any] = {}
    projection: Optional[Dict[str, int]] = None
    sort: Optional[Dict[str, int]] = None
    limit: Optional[int] = None
    skip: Optional[int] = None
    pipeline: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "operation": "find",
                    "collection": "products",
                    "filter": { "product_id": 1 },
                    "projection": None,
                    "sort": None,
                    "limit": None,
                    "skip": None,
                    "pipeline": None,
                    "explanation": "Find all products with ID 1"
                },
                {
                    "operation": "aggregate",
                    "collection": "products",
                    "pipeline": [
                        { "$match": { "in_stock": True } },
                        { "$sort": { "price": -1 } }
                    ],
                    "explanation": "Aggregate pipeline: match in-stock products and sort by price descending"
                }
            ]
        }

class QueryValidationResult(BaseModel):
    is_valid: bool = Field(description="Whether the query is syntactically correct and uses only read operations (find or aggregate). Write operations like insert, update, delete, replace, drop are invalid.")
    issues: Optional[List[str]] = Field(description="List of issues found when query is invalid")