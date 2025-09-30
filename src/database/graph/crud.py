from .db import get_graph_db

def get_graph_schema():
    graph = get_graph_db()
    graph.refresh_schema()
    return graph.schema