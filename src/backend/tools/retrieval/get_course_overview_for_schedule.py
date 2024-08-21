from tools.retrieval.helpers.db import get_nodes_of_label

import json

def get_course_overview_for_schedule(schedule_id: int) -> list:
    """Gets an overview of a schedule provided its ID.

    Args:
        schedule_id (int): The schedule ID to get the course overview for.
    
    Returns:
        list: Courses overview
    """
    schedules = get_nodes_of_label("Schedule")
    schedule = None
    for s in schedules:
        if s['schedule_id'] == schedule_id:
            schedule = s
            break
    if not schedule:
        raise Exception("Schedule not found.")
    schedule = json.loads(schedule['schedule'])
    return schedule
