"""Api for interacting with rooms"""


from threading import Thread

from flask import Blueprint, jsonify, request, g
from sqlalchemy.orm import joinedload
from ..socketio import emit_event
from ..models import Session, Room, Source, Organization, User
from ..decorators import (
    json_data_required,
    auth_required,
    admin_only,
    one_organization,
)


api = Blueprint("organizations_api", __name__)


@api.route("/organizations", methods=["GET"])
def get_all_organizations():
    organizations = g.session.query(Organization).all()
    return jsonify([item.to_dict() for item in organizations])


@api.route("/organizations/<organization_name>", methods=["POST"])
@auth_required
@admin_only
def create_organization(user, organization_name):
    organization = (
        g.session.query(Organization).filter_by(name=organization_name).first()
    )
    if organization:
        return (
            jsonify({"error": f"Organization '{organization_name}' already exist"}),
            409,
        )
    organization = Organization(name=organization_name)
    g.session.add(organization)
    user = (
        g.session.query(User)
        .options(joinedload(User.organization))
        .filter_by(id=user.id)
        .first()
    )
    user.organization = organization
    g.session.commit()

    emit_event("add_organization", {"organization": organization.name})

    return jsonify({"message": f"Created'{organization_name}'"}), 204


@api.route("/organizations/<organization_name>", methods=["DELETE"])
@auth_required
@admin_only
@one_organization
def delete_organization(organization_name):
    organization = (
        g.session.query(Organization).filter_by(name=organization_name).first()
    )
    if not organization:
        return (
            jsonify({"error": "No organization found with given organization_name"}),
            400,
        )

    g.session.delete(organization)
    g.session.commit()

    emit_event("delete_organization", {"name": organization.name})

    return jsonify({"message": "Organization deleted"}), 200


@api.route("/organizations/<organization_name>", methods=["PUT"])
@auth_required
@admin_only
@one_organization
@json_data_required
def update_organization(organization_name):
    post_data = request.get_json()
    if not post_data.get("name"):
        return jsonify({"message": "organization name is not provided"})

    organization = (
        g.session.query(Organization).filter_by(name=organization_name).first()
    )
    if not organization:
        return (
            jsonify({"error": "No organization found with given organization_name"}),
            400,
        )

    organization.name = post_data.get("name")

    emit_event("update_organization", {"name": organization.name})

    g.session.commit()

    return jsonify({"message": "Organization updated"}), 200