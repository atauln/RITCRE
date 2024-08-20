from helpers.schedule import get_schedule_link

def get_schedule_link(schedule: list[dict]) -> str:
    """Get a link to a schedule. This should be done after getting a schedule from get_potential_schedules.

    Args:
        schedule (list[dict]): The schedule to get a link for. (obtained from get_potential_schedules)

    Returns:
        str: Link to the schedule
    """
    return get_schedule_link(schedule)

if __name__ == '__main__':
    pass
