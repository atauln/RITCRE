from tools.retrieval.helpers.db import get_db

def get_courses_for_program(program: str) -> list:
    """Get courses for a program from the database.

    Args:
        program (str): The program code to get courses for.

    Returns:
        list: List of courses
    """
    db = get_db()
    query = f"MATCH (p:Program {{program_code: '{program}'}})-[:CONTAINS_COURSE]->(c:Course) RETURN c"
    results = [c['c'] for c in db.structured_query(query)]
    processed_results = [
        {
            "code": result['code'],
            "name": result['name'],
            "credits": result['credits']
        }
        for result in results
    ]
    return processed_results

if __name__ == '__main__':
    print(get_courses_for_program("SOFTENG-BS"))