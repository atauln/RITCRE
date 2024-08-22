from tools.retrieval.helpers.db import get_nodes_of_label

import json

def get_stored_schedule(schedule_id: int) -> list:
    """Get stored schedule for a schedule ID.

    Args:
        schedule_id (int): The schedule ID to get the schedule for.
    
    Returns:
        list: Schedule
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