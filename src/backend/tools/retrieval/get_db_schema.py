from tools.retrieval.helpers.db import get_db

def get_db_schema() -> str:
    """Gets the schema of the database.

    Returns:
        str: Written database schema
    """
    db = get_db()
    return db.get_schema_str()

if __name__ == '__main__':
    print(get_db_schema())
