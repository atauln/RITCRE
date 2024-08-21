from tools.retrieval.helpers.schedule import get_schedules, get_schedule_link
from tools.retrieval.helpers.db import get_db, find_max_id
import json
def get_potential_schedule(course_codes: list[str]) -> int:
    """Get potential schedule for a list of courses. It stores the schedule in the database and returns an ID for it.

    Args:
        course_codes (list[str]): The list of course codes formatted as strings.

    Returns:
        int: Potential schedule id (can be used to retrieve schedule later)
    """
    schedules = get_schedules(course_codes)
    schedule = schedules[0]
    schedule_id = find_max_id('Schedule', 'schedule_id') + 1
    db = get_db()
    query = "CREATE (s:Schedule {schedule_id: $schedule_id, schedule: $schedule}) RETURN s"
    db.structured_query(query, param_map={"schedule_id": schedule_id, "schedule": json.dumps(schedule)})
    return schedule_id

if __name__ == '__main__':
    print(get_potential_schedule(["CSCI-141", "CSCI-142"]))