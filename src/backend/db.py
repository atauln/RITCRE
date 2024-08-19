from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.graph_stores.types import EntityNode, Relation
from xml.etree import ElementTree
from alive_progress import alive_bar
import requests
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_HOST = os.getenv("NEO4J_HOST")
NEO4J_PORT = os.getenv("NEO4J_PORT")
NEO4J_DB = os.getenv("NEO4J_DB")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASS")

def fetch_url(url: str) -> ElementTree.Element:
    response = requests.get(url, stream=True)
    return ElementTree.fromstring(response.content)

def get_db() -> Neo4jPropertyGraphStore:
    return Neo4jPropertyGraphStore(
        url=f"bolt://{NEO4J_HOST}:{NEO4J_PORT}",
        database=NEO4J_DB,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD
    )

def drop_all():
    db = get_db()
    db.structured_query("MATCH (n) DETACH DELETE n;")

# UPSTREAM LOAD FUNCTIONS
def load_programs():
    db = get_db()
    tree = fetch_url("https://www.rit.edu/programs-api/?type=b&q=&college=&degree=&text=")
    with alive_bar(len(tree)) as bar:
        bar.title = 'Loading Programs'
        for program in tree:
            data = {attrib.tag: attrib.text for attrib in program}
            data['name'] = data['title']

            query = """
            MERGE (p:Program {program_code: $program_code})
            ON CREATE SET p = $data;
            """
            params = {
                "program_code": data['program_code'],
                "data": data
            }

            if data['program_code']:
                db.structured_query(query, params)
            else:
                print('No program code found for', data['name'])
            bar()
        
drop_all()
load_programs()
