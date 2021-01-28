from flask_apscheduler import APScheduler
from core.socketio import emit_event
from .models import Session, Room, Source, User
from flask import Blueprint, jsonify, request, g


def check_users(scheduler):
    def test_online():
        emit_event("check_online", {})

    scheduler.add_job(id='test_online', func=test_online, trigger='interval', seconds=5)
    scheduler.start()
