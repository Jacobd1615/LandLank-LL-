from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Date, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# Define models for LandLink Kiosk-Based Verification System


class User(db.Model):
    """Displaced individuals eligible for compensation"""

    __tablename__ = "users"

    # Primary identifier (hashed for privacy)
    hashed_user_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # All personal data stored as hashes (privacy compliance)
    hashed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_gov_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_verification_answers: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    photo_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Metadata
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    area_code: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    tokens = relationship("Token", back_populates="user")
    verification_logs = relationship("VerificationLog", back_populates="user")


class Program(db.Model):
    """Aid distribution programs for specific regions/disasters"""

    __tablename__ = "programs"

    hashed_program_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Program details
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    estimated_beneficiaries: Mapped[int] = mapped_column(Integer, nullable=False)
    area_code: Mapped[str] = mapped_column(String(50), nullable=False)

    # Time-bound distribution
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    expiration_deadline: Mapped[date] = mapped_column(Date, nullable=False)

    # Program status (ACTIVE, SUSPENDED, EXPIRED, DUMPED)
    program_status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Anti-gaming enforcement
    violation_count: Mapped[int] = mapped_column(Integer, default=0)
    suspension_reason: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relationships
    tokens = relationship("Token", back_populates="program")


class Token(db.Model):
    """Individual compensation tokens tied to users and programs"""

    __tablename__ = "tokens"

    token_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    hashed_user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.hashed_user_id")
    )
    program_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("programs.hashed_program_id")
    )

    # Token amounts and limits
    token_amount: Mapped[float] = mapped_column(Float(precision=2), nullable=False)
    weekly_limit: Mapped[float] = mapped_column(Float(precision=2), nullable=False)
    weekly_redeemed: Mapped[float] = mapped_column(Float(precision=2), default=0.0)

    # Geographic restrictions
    area_code: Mapped[str] = mapped_column(String(50), nullable=False)

    # Token status (ACTIVE, REDEEMED, TRANSFERRED_TO_POOL, EXPIRED)
    claim_status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Issuance tracking
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    last_redemption: Mapped[date] = mapped_column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tokens")
    program = relationship("Program", back_populates="tokens")


class VerificationLog(db.Model):
    """Audit trail for all kiosk verification attempts"""

    __tablename__ = "verification_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    hashed_user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.hashed_user_id"), nullable=True
    )
    program_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Verification details
    verification_status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # SUCCESS, FAILED, FLAGGED
    ai_confidence_score: Mapped[float] = mapped_column(
        Float(precision=3), nullable=True
    )
    dual_verification_passed: Mapped[bool] = mapped_column(nullable=True)

    # Failure tracking
    failure_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    geographic_violation: Mapped[bool] = mapped_column(default=False)

    # Kiosk and location data
    kiosk_location: Mapped[str] = mapped_column(String(100), nullable=False)
    kiosk_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # UN staff verification
    un_staff_id: Mapped[str] = mapped_column(String(100), nullable=True)
    staff_verification_photo_hash: Mapped[str] = mapped_column(
        String(255), nullable=True
    )

    # Timestamps
    verification_timestamp: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="verification_logs")


class PublicPoolToken(db.Model):
    """Tokens transferred to public pool from expired/suspended programs"""

    __tablename__ = "public_pool_tokens"

    token_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Token details
    token_amount: Mapped[float] = mapped_column(Float(precision=2), nullable=False)
    area_code: Mapped[str] = mapped_column(String(50), nullable=False)

    # Pool management
    pool_entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    claim_status: Mapped[str] = mapped_column(
        String(20), default="AVAILABLE"
    )  # AVAILABLE, CLAIMED

    # Original program tracking
    original_program_id: Mapped[str] = mapped_column(String(255), nullable=False)
    transfer_reason: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # EXPIRED, SUSPENDED

    # Claiming details
    claimed_by_user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    claimed_at: Mapped[date] = mapped_column(Date, nullable=True)
    claiming_kiosk: Mapped[str] = mapped_column(String(100), nullable=True)


class KioskSession(db.Model):
    """Active kiosk sessions for tracking concurrent users"""

    __tablename__ = "kiosk_sessions"

    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Session details
    kiosk_id: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    session_status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # ACTIVE, COMPLETED, ABANDONED

    # Verification progress
    identity_verified: Mapped[bool] = mapped_column(default=False)
    un_staff_present: Mapped[bool] = mapped_column(default=False)
    dual_photo_captured: Mapped[bool] = mapped_column(default=False)

    # Timestamps
    session_start: Mapped[date] = mapped_column(Date, nullable=False)
    last_activity: Mapped[date] = mapped_column(Date, nullable=False)
    session_end: Mapped[date] = mapped_column(Date, nullable=True)


class UnOrganization(db.Model):
    """UN organizations with oversight access"""

    __tablename__ = "un_organizations"

    org_id: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Organization details
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    authorized_regions: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # JSON array of area codes

    # Access permissions
    dashboard_access: Mapped[bool] = mapped_column(default=True)
    can_view_aggregates: Mapped[bool] = mapped_column(default=True)
    can_receive_alerts: Mapped[bool] = mapped_column(default=True)

    # Contact information
    contact_email: Mapped[str] = mapped_column(String(200), nullable=False)
    emergency_contact: Mapped[str] = mapped_column(String(200), nullable=True)

    # Metadata
    registered_at: Mapped[date] = mapped_column(Date, nullable=False)
    last_access: Mapped[date] = mapped_column(Date, nullable=True)


class Wallet(db.Model):
    """Digital wallet for token storage and transfers"""

    __tablename__ = "wallets"


class Transaction(db.Model):
    """Token redemption and transfer history"""

    __tablename__ = "transactions"


class Kiosk(db.Model):
    """Physical kiosk location and status data"""

    __tablename__ = "kiosks"


class StaffMember(db.Model):
    """UN staff verification permissions"""

    __tablename__ = "staff_members"


class AlertLog(db.Model):
    """System alerts and notifications"""

    __tablename__ = "alert_logs"


class SystemConfig(db.Model):
    """Global system settings and configuration"""

    __tablename__ = "system_config"
