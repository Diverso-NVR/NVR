"""
- creates an application instance and runs the dev server
"""

if __name__ == "__main__":
    from core.application import create_app
    app, socketio = create_app()
    socketio.run(app)
