# User routes
from .schema import (
    user_schema,
    users_schema,
    user_update_schema,
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import User, db
from . import users_bp
from app.extensions import limiter
from app.extensions import cache


# creating new user
@users_bp.route("/", methods=["POST"])
@limiter.limit("10/hour")  # Rate limit: 10 requests per hour per IP
def create_user():
    try:
        if request.json is None:
            return jsonify({"error": "No JSON data provided"}), 400
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return {"Error": e.messages}, 400

    query = select(User).where(User.hashed_gov_id == user_data.hashed_gov_id)
    if db.session.execute(query).scalar_one_or_none():
        return jsonify({"Error": "User with this government ID already exists"}), 400

    new_user = User(
        hashed_user_id=user_data.hashed_user_id,
        hashed_name=user_data.hashed_name,
        hashed_gov_id=user_data.hashed_gov_id,
        hashed_verification_answers=user_data.hashed_verification_answers,
        photo_hash=user_data.photo_hash,
        created_at=user_data.created_at,
        area_code=user_data.area_code,
    )

    db.session.add(new_user)
    db.session.commit()
    print("New user created successfully.")
    return user_schema.jsonify(new_user), 201
