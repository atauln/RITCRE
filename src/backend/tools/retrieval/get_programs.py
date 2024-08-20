from db_helper import get_db

def get_programs() -> str:
    """Gets the programs from the database.

    Returns:
        str: Written programs
    """
    db = get_db()
    query = f"MATCH (p:Program) RETURN p"
    results = [p['p'] for p in db.structured_query(query)]
    processed_results = [
        {
            "program_code": result['program_code'],
            "title": result['title'],
            "college": result['college'],
            "degree": result['degree'],
            "permalink": result['permalink']
        }
        for result in results
    ]
    return processed_results

if __name__ == '__main__':
    print(get_programs())