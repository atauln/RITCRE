from db_helper import get_db

def get_courses(filter: dict = {}) -> list:
    """Get courses from the database.

    Args:
        filters (dict, optional): Filters to apply to the query. Defaults to {}. 
            Ensure that the keys in the dictionary are properties of the Course node.

    Returns:
        list: List of courses
    """
    db = get_db()
    results = []
    if not filter:
        query = f"MATCH (c:Course) RETURN c"
        results = [c['c'] for c in db.structured_query(query)]
    else:
        query = f"MATCH (c:Course) WHERE "
        for key in filter:
            query += f"c.{key} = '{filter[key]}' AND "
        query = query[:-5] + " RETURN c"
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
    print(get_courses({"code": "CSCI-141"}))