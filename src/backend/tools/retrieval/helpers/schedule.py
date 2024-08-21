from typing import Optional
import json
import requests

# -- RMP API -- #
import ratemyprofessor
from ratemyprofessor.professor import Professor
# -- RMP API -- #

CURRENT_TERM = "20241"
RMP_SCHOOL = None

def fetch_url(url: str) -> dict:
    response = requests.get(url, stream=True, timeout=10)
    return json.loads(response.content)

def get_course_options(course_code: str) -> dict:
    url = "https://schedulemaker.csh.rit.edu/generate/getCourseOpts"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Accept': 'application/json text/plain */*'
    }
    payload = {
        "course": course_code,
        "term": CURRENT_TERM,
        "ignoreFull": "false"
    }
    session = requests.Session()
    response = session.post(url, data=payload, headers=headers)
    return response.json()

def get_schedules(course_names: list[str], time_blocks: list[tuple] = None) -> list[list[dict]]:
    # timeblocks are tuples of (start, end, days)
    if not course_names:
        return []
    payload = {
        "term": CURRENT_TERM,
        "courseCount": len(course_names),
        "noCourseCount": len(time_blocks) if time_blocks is not None else 0,
        "nonCourseCount": 0,
    }
    for i, course in enumerate(course_names):
        payload[f"courses{i+1}"] = course
        opts = get_course_options(course)
        payload[f"courses{i+1}Opt[]"] = [opt['id'] for opt in opts]
    if time_blocks is not None:
        for i, block in enumerate(time_blocks):
            payload[f"noCourseStartTime{i+1}"] = block[0]
            payload[f"noCourseEndTime{i+1}"] = block[1]
            payload[f"noCourseDays{i+1}[]"] = block[2]
    url = "https://schedulemaker.csh.rit.edu/generate/getMatchingSchedules"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Accept': 'application/json text/plain */*'
    }
    session = requests.Session()
    response = session.post(url, data=payload, headers=headers)
    return response.json()['schedules']

def get_schedule_link(schedule: list[dict]) -> Optional[str]:
    payload = {
        "data": json.dumps({
            "startday": 1,
            "endday": 5,
            "starttime": 8*60,
            "endtime": 22*60,
            "building": "code",
            "term": CURRENT_TERM,
            "schedule": schedule
        })
    }
    url = "https://schedulemaker.csh.rit.edu/schedule/new"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Accept': 'application/json text/plain */*',
        'Priority': 'u=0',
    }
    session = requests.Session()
    response = session.post(url, data=payload, headers=headers)
    if 'error' in response.json():
        return None
    return response.json()['url']

def lookup_professor(professor: str) -> Optional[Professor]:
    global RMP_SCHOOL
    if not RMP_SCHOOL:
        for school in ratemyprofessor.get_schools_by_name("Rochester Institute of Technology"):
            if school.name.upper() == "ROCHESTER INSTITUTE OF TECHNOLOGY":
                RMP_SCHOOL = school
                break
        else:
            print("[RMP] School not found")
    professor = ratemyprofessor.get_professor_by_school_and_name(RMP_SCHOOL, professor)
    return professor

if __name__ == "__main__":
    courses = ["ISTE-430-01", "SWEN-444", "SWEN-343", "CSCI-261"]
    timeblocks = [
            (15*60+30, 17*60, ["Tue", "Thu"]),
            (13*60, 17*60, ["Fri"]),
            (9*60, 11*60, ["Mon", "Tue", "Wed", "Thu", "Fri"])
    ]
    print("Fetching schedules with the following courses and timeblocks:")
    print(courses)
    print(timeblocks)
    schedules = get_schedules(
        course_names=courses, 
        time_blocks=timeblocks
    )
    print(f"Found {len(schedules)} schedules")
    print(get_schedule_link(schedules[0]))
