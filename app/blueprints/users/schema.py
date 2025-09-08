# User schemas
import re
from marshmallow import ValidationError, fields, validates
from app.extensions import ma
from app.models import User


# Defining the Marshmallow schemas for serialization and deserialization
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        exclude = ("tokens", "verification_logs")
        load_instance = True

    @validates("hashed_name")
    def validate_hashed_name(self, value, **kwargs):
        if len(value) != 64:  # SHA-256 hash length
            raise ValidationError("Invalid hash format for name.")

    @validates("hashed_gov_id")
    def validate_hashed_gov_id(self, value, **kwargs):
        if len(value) != 64:  # SHA-256 hash length
            raise ValidationError("Invalid hash format for government ID.")

    @validates("area_code")
    def validate_area_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_-]{2,10}$", value):
            raise ValidationError("Invalid area code format.")


class UserUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True

    hashed_user_id = fields.String(dump_only=True)
    created_at = fields.Date(dump_only=True)

    @validates("area_code")
    def validate_area_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_-]{2,10}$", value):
            raise ValidationError("Invalid area code format.")


# creating an instance of the schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserUpdateSchema()
