from tools.retrieval.helpers.db import get_nodes_of_label
from tools.retrieval.helpers.schedule import get_schedule_link as get_sch_link
import json

def get_schedule_link(schedule_id: int) -> str:
    """Get schedule link for a schedule ID.

    Args:
        schedule_id (int): The schedule ID to get the link for.
    
    Returns:
        str: Schedule link
    """
    schedules = get_nodes_of_label("Schedule")
    schedule = None
    for s in schedules:
        if s['schedule_id'] == schedule_id:
            schedule = s
            break
    if not schedule:
        raise Exception("Schedule not found.")
    try:
        schedule_link = get_sch_link(json.loads(schedule['schedule']))
    except:
        raise Exception("Unable to generate URL for schedule. Please try again later.")
    return schedule_link

if __name__ == '__main__':
    print(get_schedule_link(3))