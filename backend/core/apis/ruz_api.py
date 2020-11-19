import requests
from datetime import datetime

RUZ_API_URL = "http://92.242.58.221/ruzservice.svc"


# building id МИЭМа = 92
def get_all_rooms(building_id: int = 92) -> list:
    try:
        res = requests.get(f"{RUZ_API_URL}/auditoriums?buildingoid=0")
    except Exception:
        return []

    for room in res.json():
        if (
            room["buildingGid"] == building_id
            and room["typeOfAuditorium"] != "Неаудиторные"
        ):
            yield room


def get_room_ruzid(room_name: int) -> int:
    try:
        return next(
            room["auditoriumOid"]
            for room in get_all_rooms()
            if str(room["number"]) == room_name
        )
    except StopIteration:
        return None


def get_classes(ruz_room_id: str, start_time: datetime, end_time: datetime):
    format = "%Y.%m.%d %H:%M"
    params = dict(
        fromdate=start_time.isoformat(),
        todate=end_time.isoformat(),
        auditoriumoid=ruz_room_id,
    )

    res = requests.get(f"{RUZ_API_URL}/lessons", params=params)
    for class_ in res.json():
        ruz_start_time = datetime.strptime(
            class_["date"] + " " + class_["beginLesson"], format
        )
        ruz_end_time = datetime.strptime(
            class_["date"] + " " + class_["endLesson"], format
        )

        if (
            ruz_end_time >= start_time
            and end_time >= ruz_start_time
            and ruz_start_time >= start_time
        ):
            class_["startTime"] = ruz_start_time.isoformat()
            class_["endTime"] = ruz_end_time.isoformat()
            yield class_
