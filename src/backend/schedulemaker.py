import requests
from alive_progress import alive_bar
import json

from multiprocessing import Pool


CURRENT_TERM = "20241"

def fetch_url(url: str) -> dict:
    response = requests.get(url, stream=True)
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

def get_schedules(courses: list[str], timeblocks: list[tuple] = []) -> list[dict]:
    # timeblocks are tuples of (start, end, days)
    payload = {
        "term": CURRENT_TERM,
        "courseCount": len(courses),
        "noCourseCount": len(timeblocks),
        "nonCourseCount": 0,
    }
    for i, course in enumerate(courses):
        payload[f"courses{i+1}"] = course
        opts = get_course_options(course)
        payload[f"courses{i+1}Opt[]"] = [opt['id'] for opt in opts]
    for i, block in enumerate(timeblocks):
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

def get_schedule_link(schedule: list[dict]) -> str:
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
        
if __name__ == "__main__":
    schedules = get_schedules(
        courses=["ISTE-430-01", "SWEN-444", "SWEN-343", "CSCI-261"], 
        timeblocks=[
            (15*60+30, 17*60, ["Tue", "Thu"]), 
            (13*60, 17*60, ["Fri"]), 
            (9*60, 11*60, ["Mon", "Tue", "Wed", "Thu", "Fri"])]
    )
    print(f"Found {len(schedules)} schedules")
    print(get_schedule_link(schedules[0]))
