"""
- creates an application instance and runs the dev server
"""

if __name__ == "__main__":
    from core.application import create_app
    from core.online import check_users

    app, socketio, scheduler = create_app()
    check_users(scheduler)
    socketio.run(app)





