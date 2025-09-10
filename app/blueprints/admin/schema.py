# Admin schemas
import re
from marshmallow import ValidationError, fields, validates
from app.extensions import ma
from app.models import Admin


# Defining the Marshmallow schemas for serialization and deserialization
class AdminSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Admin
        include_fk = True
        exclude = ("hashed_password",)  # Never include password in responses
        load_instance = True

    @validates("admin_email")
    def validate_email(self, value, **kwargs):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValidationError("Invalid email format.")

    @validates("admin_username")
    def validate_username(self, value, **kwargs):
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValidationError(
                "Username can only contain letters, numbers, hyphens, and underscores."
            )

    @validates("hashed_password")
    def validate_password(self, value, **kwargs):
        if len(value) < 12:
            raise ValidationError("Admin password must be at least 12 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[a-z]", value):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r"\d", value):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValidationError(
                "Password must contain at least one special character."
            )

    @validates("admin_role")
    def validate_admin_role(self, value, **kwargs):
        allowed_roles = ["CEO", "ADMIN", "SECURITY_ADMIN"]
        if value not in allowed_roles:
            raise ValidationError(
                f"Admin role must be one of: {', '.join(allowed_roles)}"
            )

    @validates("clearance_level")
    def validate_clearance_level(self, value, **kwargs):
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValidationError("Clearance level must be an integer between 1 and 5.")

    @validates("ip_whitelist")
    def validate_ip_whitelist(self, value, **kwargs):
        if value:
            # Basic IP validation for JSON array format
            if not value.startswith("[") or not value.endswith("]"):
                raise ValidationError("IP whitelist must be a valid JSON array format.")

    @validates("authorized_regions")
    def validate_authorized_regions(self, value, **kwargs):
        if value and value != "ALL":
            if not value.startswith("[") or not value.endswith("]"):
                raise ValidationError(
                    "Authorized regions must be 'ALL' or a valid JSON array format."
                )


class AdminUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Admin
        include_fk = True
        exclude = (
            "admin_id",
            "created_at",
            "created_by_admin_id",
        )  # Prevent updating these fields
        load_instance = True

    admin_id = fields.String(dump_only=True)
    created_at = fields.Date(dump_only=True)
    hashed_password = fields.String(load_only=True, required=False)

    @validates("admin_email")
    def validate_email(self, value, **kwargs):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValidationError("Invalid email format.")

    @validates("hashed_password")
    def validate_password(self, value, **kwargs):
        if value and len(value) < 12:
            raise ValidationError("Admin password must be at least 12 characters long.")

    @validates("admin_role")
    def validate_admin_role(self, value, **kwargs):
        allowed_roles = ["CEO", "ADMIN", "SECURITY_ADMIN"]
        if value not in allowed_roles:
            raise ValidationError(
                f"Admin role must be one of: {', '.join(allowed_roles)}"
            )

    @validates("clearance_level")
    def validate_clearance_level(self, value, **kwargs):
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValidationError("Clearance level must be an integer between 1 and 5.")


class AdminLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Admin
        include_fk = False
        load_instance = False

    admin_username = fields.String(required=True)
    hashed_password = fields.String(required=True, load_only=True)

    @validates("admin_username")
    def validate_username(self, value, **kwargs):
        if not value:
            raise ValidationError("Username is required.")

    @validates("hashed_password")
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError("Password is required.")


class AdminPermissionsSchema(ma.SQLAlchemyAutoSchema):
    """Schema for viewing/updating admin permissions only"""

    class Meta:
        model = Admin
        include_fk = False
        load_instance = True
        include = (
            "admin_id",
            "admin_username",
            "admin_role",
            "clearance_level",
            "can_create_programs",
            "can_delete_programs",
            "can_suspend_users",
            "can_override_security",
            "can_access_all_logs",
            "can_modify_system_config",
            "can_emergency_shutdown",
            "can_manage_organizations",
            "can_view_all_transactions",
            "can_force_token_redistribution",
            "can_reset_user_passwords",
            "can_access_raw_data",
            "unrestricted_area_access",
        )

    admin_id = fields.String(dump_only=True)
    admin_username = fields.String(dump_only=True)


# Creating instances of the schemas
admin_schema = AdminSchema()
admins_schema = AdminSchema(
    many=True, exclude=("hashed_password", "ip_whitelist", "notes")
)
admin_login_schema = AdminLoginSchema()
admin_update_schema = AdminUpdateSchema()
admin_permissions_schema = AdminPermissionsSchema()
