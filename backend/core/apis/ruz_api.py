import requests

RUZ_API_URL = "http://92.242.58.221/ruzservice.svc"


# building id МИЭМа = 92
def get_all_rooms(building_id: int = 92) -> list:
    try:
        all_auditories = requests.get(f"{RUZ_API_URL}/auditoriums?buildingoid=0").json()
    except Exception:
        return []

    return [
        room
        for room in all_auditories
        if room["buildingGid"] == building_id
        and room["typeOfAuditorium"] != "Неаудиторные"
    ]


def get_room_ruzid(room_name: int) -> int:
    rooms = get_all_rooms()

    try:
        return next(
            room["auditoriumOid"] for room in rooms if str(room["number"]) == room_name
        )
    except StopIteration:
        return None
