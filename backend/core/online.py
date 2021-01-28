from core.socketio import emit_event


def check_users(scheduler):
    def test_online():
        emit_event("check_online", {})

    scheduler.add_job(id="test_online", func=test_online, trigger="interval", seconds=5)
    scheduler.start()
