from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.graph_stores.types import EntityNode, Relation
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError as XMLParseError
from multiprocessing import Pool
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
    db.structured_query("MATCH (n) DETACH DELETE n")

def get_nodes_of_label(label: str) -> list[EntityNode]:
    db = get_db()
    return db.structured_query(f"MATCH (n:{label}) RETURN n")

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
            ON CREATE SET p = $data
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

def load_courses(program_code: str):
    db = get_db()
    try:
        tree = fetch_url(f"https://www.rit.edu/programs-api/?type=p&q={program_code}&college=&degree=&text=2")
    except XMLParseError:
        print('Could not fetch courses for', program_code)
        return
    tbody = tree.find('./program/curriculum/table/tbody')
    if not tbody:
        print('No courses found for', program_code)
        return
    with alive_bar(len(tbody)) as bar:
        for tr in tbody:
            if len(tr.findall('td')) < 3 or len(tr.find('td').attrib) > 0:
                continue
            values = tr.findall('td')
            course_code = values[0].text
            course_name = values[1].text
            course_credits = values[2].text
            if len(course_code) < 3:
                course_code = course_name.replace(" ", "").upper()[:-1]

            query = """
            MERGE (c:Course {course_code: $course_code})
            ON CREATE SET c = $data
            MERGE (p:Program {program_code: $program_code})
            MERGE (p)-[:CONTAINS_COURSE]->(c)
            """
            params = {
                "course_code": course_code,
                "program_code": program_code,
                "data": {
                    "course_code": course_code,
                    "course_name": course_name,
                    "course_credits": course_credits
                }
            }

            db.structured_query(query, params)
            bar()

def load():
    drop_all()
    load_programs()
    programs = get_nodes_of_label('Program')
    with Pool(8) as p:
        p.map(load_courses, [program['n']['program_code'] for program in programs])

load()
