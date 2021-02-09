from core.socketio import emit_event


def check_users(scheduler):
    def kick():
        emit_event("kick_banned", {})

    def check_online():
        emit_event("check_online", {})

    scheduler.add_job(id="kick_ban", func=kick, trigger="interval", seconds=5)
    scheduler.add_job(id="check", func=check_online, trigger="interval", seconds=10)
    scheduler.start()
