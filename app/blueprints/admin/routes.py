# Admin routes
from .schema import (
    admin_schema,
    admins_schema,
    admin_login_schema,
    admin_update_schema,
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Admin, db
from . import admin_bp
from app.extensions import limiter
from app.extensions import cache
from datetime import date
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


# creating new admin
@admin_bp.route("/", methods=["POST"])
@limiter.limit("10/hour")  # Rate limit: 10 requests per hour per IP
def create_admin():
    try:
        if request.json is None:
            return jsonify({"error": "No JSON data provided"}), 400
        admin_data = admin_schema.load(request.json)
    except ValidationError as e:
        return {"Error": e.messages}, 400

    # Check if admin with this email already exists
    query = select(Admin).where(Admin.admin_email == request.json.get("admin_email"))
    if db.session.execute(query).scalar_one_or_none():
        return jsonify({"Error": "Admin with this email already exists"}), 400

    # Check if admin with this username already exists
    query = select(Admin).where(
        Admin.admin_username == request.json.get("admin_username")
    )
    if db.session.execute(query).scalar_one_or_none():
        return jsonify({"Error": "Admin with this username already exists"}), 400

    password = request.json.get("hashed_password")
    if not password:
        return jsonify({"Error": "Password is required."}), 400

    new_admin = Admin()
    new_admin.admin_id = str(uuid.uuid4())  # Generate unique admin ID
    new_admin.admin_username = request.json.get("admin_username")
    new_admin.admin_email = request.json.get("admin_email")
    new_admin.hashed_password = generate_password_hash(password)  # Now properly hashed!
    new_admin.admin_role = request.json.get("admin_role", "SUPER_ADMIN")
    new_admin.clearance_level = request.json.get("clearance_level", 5)
    new_admin.created_at = date.today()
    new_admin.is_active = True

    # Set all the powerful admin permissions to True by default
    new_admin.can_create_programs = True
    new_admin.can_delete_programs = True
    new_admin.can_suspend_users = True
    new_admin.can_override_security = True
    new_admin.can_access_all_logs = True
    new_admin.can_modify_system_config = True
    new_admin.can_emergency_shutdown = True
    new_admin.can_manage_organizations = True
    new_admin.can_view_all_transactions = True
    new_admin.can_force_token_redistribution = True
    new_admin.can_reset_user_passwords = True
    new_admin.can_access_raw_data = True
    new_admin.unrestricted_area_access = True
    new_admin.mfa_enabled = True
    new_admin.authorized_regions = "ALL"

    db.session.add(new_admin)
    db.session.commit()
    print("New admin created successfully.")
    return admin_schema.jsonify(new_admin), 201


@admin_bp.route("/login", methods=["POST"])
@limiter.limit("5/minute")  # Rate limit: 5 login attempts per minute per IP
def admin_login():
    """Admin login with password verification"""
    try:
        if request.json is None:
            return jsonify({"error": "No JSON data provided"}), 400
        login_data = admin_login_schema.load(request.json)
    except ValidationError as e:
        return {"Error": e.messages}, 400

    username = request.json.get("admin_username")
    password = request.json.get("hashed_password")

    if not username or not password:
        return jsonify({"Error": "Username and password are required"}), 400

    # Find admin by username
    query = select(Admin).where(Admin.admin_username == username)
    admin = db.session.execute(query).scalar_one_or_none()

    if not admin:
        return jsonify({"Error": "Invalid credentials"}), 401

    # Check if account is active
    if not admin.is_active:
        return jsonify({"Error": "Account is deactivated"}), 401

    # Verify password using check_password_hash
    if not check_password_hash(admin.hashed_password, password):
        # Increment failed login attempts
        admin.failed_login_attempts += 1
        if admin.failed_login_attempts >= 5:
            admin.account_locked = True
        db.session.commit()
        return jsonify({"Error": "Invalid credentials"}), 401

    # Check if account is locked
    if admin.account_locked:
        return (
            jsonify({"Error": "Account is locked due to too many failed attempts"}),
            401,
        )

    # Successful login - reset failed attempts and update last login
    admin.failed_login_attempts = 0
    admin.last_login = date.today()
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Login successful",
                "admin_id": admin.admin_id,
                "admin_username": admin.admin_username,
                "admin_role": admin.admin_role,
                "clearance_level": admin.clearance_level,
            }
        ),
        200,
    )
