import os
import re
from subprocess import Popen, check_output
from typing import Set

from flask import Blueprint, jsonify, request, g, redirect

from ..decorators import auth_required, admin_only
from ..models import Autorecord

api = Blueprint("management_api", __name__)

default_days = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
}


# Паттерн для валидации подстрок HH:MM - в текущей реализации не нужен, но пусть лежит на всякий
time_pattern = re.compile("^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")


@api.route("/autorec-deploy", methods=["PUT"])
@auth_required
@admin_only
def deploy_autorec(current_user):
    body = request.get_json()

    if not body:
        return jsonify({"error", "No request body provided"}), 400

    days: Set[str] = body["record_days"]

    if not all(x in default_days for x in days):
        return jsonify({"error": "Error in field 'record_days'"}), 400

    duration: int = body["duration"]

    if duration < 10:
        return jsonify({"error": "Duration cannot be less that 10 minutes"}, 400)

    record_start: int = body["record_start"]
    record_end: int = body["record_end"]

    if record_start < 0 or record_start > record_end:
        return jsonify({"error": "Wrong start/end parameters"}, 400)

    upload_without_sound: bool = bool(body["upload_without_sound"])

    autorec_name = "nvr_autorec_" + current_user.email.replace("@", "_")

    if not create_env_file(autorec_name, days, duration,
                           record_start, record_end,
                           upload_without_sound):
        return jsonify({"error": f"Error while creating environment file .env_nvr_autorec_{current_user.email}"}, 400)

    process = Popen(["../scripts/deploy_autorec.sh", autorec_name])
    # TODO можно проследить по пиду чё с процессом

    new_autorec = Autorecord(name=autorec_name, days=",".join(str(day) for day in days),
                             duration=duration, record_start=record_start, record_end=record_end,
                             upload_without_sound=upload_without_sound, user_id=current_user.id)

    autorec = g.session.query(Autorecord).filter_by(name=autorec_name).first()

    if autorec:
        autorec.update(new_autorec)
    else:
        g.session.add(new_autorec)
    g.session.commit()

    return jsonify({"message": "Deployment started"}, 200)


@api.route("/autorec-monitoring", methods=["GET"])
@auth_required
@admin_only
def get_monitoring_link(current_user):
    autorec_name = "nvr_autorec_" + current_user.email.replace("@", "_")

    autorec = g.session.query(Autorecord).filter_by(name=autorec_name).first()

    if not autorec:
        return jsonify({"error": "No active autorecord instance"}, 404)

    container_id = check_output(["docker", "inspect", "--format=\"{{.Id}}\"", autorec_name])

    return redirect(os.environ.get("C_ADVISOR_URL") + "/docker/" + container_id, 302)


@api.route("/autorec-config", methods=["GET"])
@auth_required
@admin_only
def get_autorecord_config(current_user):
    autorec = g.session.query(Autorecord).filter_by(name="nvr_autorec_" + current_user.email.replace("@", "_")).first()

    if not autorec:
        return jsonify({"error": "No active autorecord instance"}, 404)

    return jsonify(autorec.to_dict(), 200)


def create_env_file(autorec_name: str, days: Set, duration: int,
                    record_start: int, record_end: int,
                    upload_without_sound: bool):
    env_file = open("/env_files/.env_" + autorec_name, "w")

    try:
        env_file.writelines([
            "GOOGLE_DRIVE_TOKEN_PATH=/autorecord/creds/tokenDrive.pickle",
            "GOOGLE_DRIVE_SCOPES=[\"https://www.googleapis.com/auth/drive\"]",
            "PSQL_URL=" + os.environ.get("DB_URL"),
            "NVR_API_URL=" + os.environ.get("NVR_API_URL"),
            "NVR_API_KEY=" + os.environ.get("NVR_API_KEY"),
            "LOGURU_LEVEL=INFO",
            "RECORD_DAYS=[{}]".format(", ".join(str(day) for day in days)),
            "RECORD_DURATION=" + str(duration),
            "RECORD_START=" + str(record_start),
            "RECORD_END=" + str(record_end),
            "UPLOAD_WITHOUT_SOUND=" + str(upload_without_sound)
        ])
    except:
        return False
    finally:
        env_file.close()

    return True
