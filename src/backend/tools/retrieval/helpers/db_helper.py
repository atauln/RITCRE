from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_HOST = os.getenv("NEO4J_HOST")
NEO4J_PORT = os.getenv("NEO4J_PORT")
NEO4J_DB = os.getenv("NEO4J_DB")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASS")

GRAPH_STORE = None


def get_db() -> Neo4jPropertyGraphStore:
    GRAPH_STORE = None
    if not GRAPH_STORE:
        GRAPH_STORE = Neo4jPropertyGraphStore(
            url=f"bolt://{NEO4J_HOST}:{NEO4J_PORT}",
            database=NEO4J_DB,
            username=NEO4J_USER,
            password=NEO4J_PASSWORD
        )
    return GRAPH_STORE