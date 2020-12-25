import requests
from datetime import datetime

RUZ_API_URL = "http://92.242.58.221/ruzservice.svc"
NVR_ERUDITE_API_URL = "https://nvr.miem.hse.ru/api/erudite"

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


def get_classes(ruz_auditorium: str, start_time: datetime, end_time: datetime):
    params = dict(
        ruz_auditorium=ruz_auditorium,
        fromdate=start_time.isoformat(),
        todate=end_time.isoformat(),
    )

    res = requests.get(f"{NVR_ERUDITE_API_URL}/lessons", params=params)
    for class_ in res.json():
        yield class_
