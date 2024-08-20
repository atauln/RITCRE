from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.graph_stores.types import LabelledNode, Relation
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

NUM_PROCESSES = int(os.getenv("NUM_PROCESSES"))

GRAPH_STORE = None

def fetch_url(url: str) -> ElementTree.Element:
    response = requests.get(url, stream=True)
    return ElementTree.fromstring(response.content)

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

def drop_all(db: Neo4jPropertyGraphStore = None):
    if not db:
        db = get_db()
    db.structured_query("MATCH (n) DETACH DELETE n")

def get_nodes_of_label(label: str, db: Neo4jPropertyGraphStore = None) -> list[LabelledNode]:
    if not db:
        db = get_db()
    return [n['n'] for n in db.structured_query(f"MATCH (n:{label}) RETURN n")]

# UPSTREAM LOAD FUNCTIONS
def load_programs(db: Neo4jPropertyGraphStore = None):
    tree = fetch_url("https://www.rit.edu/programs-api/?type=b&q=&college=&degree=&text=")
    with alive_bar(len(tree)) as bar:
        bar.title = 'Loading Programs'
        if not db:
            db = get_db()
        for program in tree:
            data = {attrib.tag: attrib.text for attrib in program}
            data['name'] = data['title']
            for key in data:
                if key == 'title':
                    continue
                data[key] = data[key].strip() if data[key] else None

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

def load_courses(program_code: str, db: Neo4jPropertyGraphStore = None):
    try:
        tree = fetch_url(f"https://www.rit.edu/programs-api/?type=p&q={program_code}&college=&degree=&text=2")
    except XMLParseError:
        print('Could not fetch courses for', program_code)
        return
    tbody = tree.find('./program/curriculum/table/tbody')
    if tbody is None: # required to be written this way
        print('No courses found for', program_code)
        return
    for tr in tbody:
        if len(tr.findall('td')) < 3 or len(tr.find('td').attrib) > 0:
            continue
        values = tr.findall('td')
        course_code = values[0].text
        course_name = values[1].text
        course_credits = values[2].text
        if len(course_code) < 3:
            course_code = course_name.replace(" ", "").upper()
            course_code += f"-{program_code}" if course_code == "OPENELECTIVES" else ""

        if not db:
            db = get_db()
        query = """
        MERGE (c:Course {code: $course_code})
        ON CREATE SET c = $data
        MERGE (p:Program {program_code: $program_code})
        MERGE (p)-[:CONTAINS_COURSE]->(c)
        """
        params = {
            "course_code": course_code.strip(),
            "program_code": program_code.strip(),
            "data": {
                "code": course_code.strip(),
                "name": course_name.strip(),
                "credits": course_credits.strip()
            }
        }

        db.structured_query(query, params)


def load_course_info(course_code: str, db: Neo4jPropertyGraphStore = None):
    if len(course_code) > 8 or len(course_code) < 3:
        return
    try:
        tree = fetch_url(f"https://www.rit.edu/programs-api/?type=c&q={course_code}&college=&degree=&text=")
    except XMLParseError:
        print('Could not fetch course info for', course_code)
        return
    course = tree.find('./course')
    if course is None:
        print('No course found for', course_code)
        return
    course_description = course.find('description').text if course.find('description') is not None else "No description available"
    typically_offered = course.find('typically_offered').text if course.find('typically_offered') is not None else "Not specified"
    course_prerequisites = course.find('requisites').text if course.find('requisites') is not None else "None"
    if not course_description:
        course_description = "No description available"
    if not typically_offered:
        typically_offered = "Not specified"
    if not course_prerequisites:
        course_prerequisites = "None"
    course_prerequisites = course_prerequisites.replace("Prerequisite: ", "").replace(" or equivalent course.", "")

    if not db:
        db = get_db()
    
    query = """
    MERGE (c:Course {code: $course_code})
    SET c += $data
    """
    params = {
        "course_code": course_code,
        "data": {
            "description": course_description.strip(),
            "typically_offered": typically_offered.strip(),
            "prerequisites": course_prerequisites.strip()
        }
    }

    db.structured_query(query, params)

def load(graph_store: Neo4jPropertyGraphStore = None):
    if not graph_store:
        graph_store = get_db()
    drop_all(graph_store)
    load_programs(graph_store)
    programs = get_nodes_of_label('Program', graph_store)
    with Pool(NUM_PROCESSES) as p:
        with alive_bar(len(programs)) as bar:
            bar.title = 'Loading Courses'
            p.map(load_courses, [program['program_code'] for program in programs])
            for _ in range(len(programs)):
                bar()
    courses = get_nodes_of_label('Course')
    with Pool(NUM_PROCESSES) as p:
        with alive_bar(len(courses)) as bar:
            bar.title = 'Loading Course Info'
            p.map(load_course_info, [course['code'] for course in courses])
            for _ in range(len(courses)):
                bar()
if __name__ == "__main__":
    load()
