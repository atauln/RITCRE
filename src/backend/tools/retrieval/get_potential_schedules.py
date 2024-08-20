from helpers.schedule import get_schedules

def get_potential_schedules(course_codes: list[str], time_blocks: list[tuple] = None) -> list[dict]:
    """Get potential schedules for a list of courses.

    Args:
        course_codes (list[str]): The list of course codes.
        time_blocks (list[tuple], optional): The list of time blocks to avoid. Defaults to None.
            time blocks should be formatted as tuples of 
                (start (in minutes from 0:00), end (in minutes from 0:00), days).

    Returns:
        list[dict]: List of potential schedules
    """
    return get_schedules(course_codes, time_blocks)

if __name__ == '__main__':
    print(get_potential_schedules(["CSCI-141", "CSCI-142"]))