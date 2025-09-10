from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Date, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# Define models for LandLink System


class Admin(db.Model):
    """System administrators with full system control and oversight"""

    __tablename__ = "admins"

    admin_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    admin_username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    admin_email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    # Enhanced admin roles and hierarchy
    admin_role: Mapped[str] = mapped_column(
        String(50), default="CEO"
    )  # CEO, ADMIN, SECURITY_ADMIN
    clearance_level: Mapped[int] = mapped_column(
        Integer, default=5
    )  # Highest clearance level

    # Full system permissions
    can_create_programs: Mapped[bool] = mapped_column(default=True)
    can_delete_programs: Mapped[bool] = mapped_column(default=True)
    can_suspend_users: Mapped[bool] = mapped_column(default=True)
    can_override_security: Mapped[bool] = mapped_column(default=True)
    can_access_all_logs: Mapped[bool] = mapped_column(default=True)
    can_modify_system_config: Mapped[bool] = mapped_column(default=True)
    can_emergency_shutdown: Mapped[bool] = mapped_column(default=True)
    can_manage_organizations: Mapped[bool] = mapped_column(default=True)
    can_view_all_transactions: Mapped[bool] = mapped_column(default=True)
    can_force_token_redistribution: Mapped[bool] = mapped_column(default=True)
    can_reset_user_passwords: Mapped[bool] = mapped_column(default=True)
    can_access_raw_data: Mapped[bool] = mapped_column(default=True)

    # Geographic oversight (admins can override all area restrictions)
    unrestricted_area_access: Mapped[bool] = mapped_column(default=True)
    authorized_regions: Mapped[str] = mapped_column(
        String(1000), default="ALL"
    )  # JSON array or "ALL"

    # Security and monitoring
    mfa_enabled: Mapped[bool] = mapped_column(
        default=True
    )  # Multi-factor authentication required
    ip_whitelist: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # JSON array of allowed IPs
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    account_locked: Mapped[bool] = mapped_column(default=False)

    # Activity tracking
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    last_login: Mapped[date] = mapped_column(Date, nullable=True)
    last_action_timestamp: Mapped[date] = mapped_column(Date, nullable=True)
    total_actions_performed: Mapped[int] = mapped_column(Integer, default=0)

    # Status and accountability
    is_active: Mapped[bool] = mapped_column(default=True)
    created_by_admin_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Admin who created this account
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)  # Internal notes


class Employee(db.Model):
    """General system employees with role-based access"""

    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    employee_username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_email: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True
    )
    employee_role: Mapped[str] = mapped_column(String(50), default="EMPLOYEE")
    login_location_IP: Mapped[int] = mapped_column(Integer, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    last_login: Mapped[date] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class Client(db.Model):
    """Clients or beneficiaries of the system"""

    __tablename__ = "clients"

    client_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_email: Mapped[str] = mapped_column(String(200), nullable=True)
    client_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    area_code: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    login_location_IP: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    tokens = relationship("Token", back_populates="client")
    verification_logs = relationship("VerificationLog", back_populates="client")
    wallets = relationship("Wallet", back_populates="client")


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
    client_id: Mapped[str] = mapped_column(String(255), ForeignKey("clients.client_id"))
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
    client = relationship("Client", back_populates="tokens")
    program = relationship("Program", back_populates="tokens")
    transactions = relationship("Transaction", back_populates="token")


class VerificationLog(db.Model):
    """Audit trail for all kiosk verification attempts"""

    __tablename__ = "verification_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    client_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("clients.client_id"), nullable=True
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
    kiosk_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("kiosks.kiosk_id"), nullable=False
    )

    # Field worker verification
    supervisor_id: Mapped[str] = mapped_column(String(100), nullable=True)
    supervisor_verification_photo_hash: Mapped[str] = mapped_column(
        String(255), nullable=True
    )

    # Timestamps
    verification_timestamp: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="verification_logs")
    kiosk = relationship("Kiosk", back_populates="verification_logs")


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
    kiosk_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("kiosks.kiosk_id"), nullable=False
    )
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

    # Relationships
    kiosk = relationship("Kiosk", back_populates="sessions")


class Organization(db.Model):
    """Organizations with oversight access"""

    __tablename__ = "organizations"

    org_id: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Organization details
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # NGO, GOVERNMENT, PRIVATE, etc.
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

    # Relationships
    supervisors = relationship("Supervisor", back_populates="organization")


class Wallet(db.Model):
    """Digital wallet for token storage and transfers"""

    __tablename__ = "wallets"

    wallet_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Client association
    client_id: Mapped[str] = mapped_column(String(255), ForeignKey("clients.client_id"))

    # Wallet details
    wallet_balance: Mapped[float] = mapped_column(Float(precision=2), default=0.0)
    total_tokens_received: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_redeemed: Mapped[int] = mapped_column(Integer, default=0)

    # Security
    wallet_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_transaction_hash: Mapped[str] = mapped_column(String(255), nullable=True)

    # Metadata
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    last_activity: Mapped[date] = mapped_column(Date, nullable=True)

    # Status
    wallet_status: Mapped[str] = mapped_column(
        String(20), default="ACTIVE"
    )  # ACTIVE, SUSPENDED, CLOSED

    # Relationships
    client = relationship("Client", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(db.Model):
    """Token redemption and transfer history"""

    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    wallet_id: Mapped[str] = mapped_column(String(255), ForeignKey("wallets.wallet_id"))
    token_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("tokens.token_id"), nullable=True
    )
    kiosk_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("kiosks.kiosk_id"), nullable=True
    )

    # Transaction details
    transaction_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # REDEMPTION, TRANSFER, ISSUANCE
    transaction_amount: Mapped[float] = mapped_column(
        Float(precision=2), nullable=False
    )
    transaction_status: Mapped[str] = mapped_column(
        String(20), default="PENDING"
    )  # PENDING, COMPLETED, FAILED

    # Security and verification
    transaction_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    verification_signature: Mapped[str] = mapped_column(String(255), nullable=True)

    # Location and timing
    transaction_location: Mapped[str] = mapped_column(String(100), nullable=True)
    transaction_timestamp: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[date] = mapped_column(Date, nullable=True)

    # Failure handling
    failure_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    token = relationship("Token", back_populates="transactions")
    kiosk = relationship("Kiosk", back_populates="transactions")


class Kiosk(db.Model):
    """Physical kiosk location and status data"""

    __tablename__ = "kiosks"

    kiosk_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Location details
    kiosk_location: Mapped[str] = mapped_column(String(200), nullable=False)
    area_code: Mapped[str] = mapped_column(String(50), nullable=False)
    gps_coordinates: Mapped[str] = mapped_column(String(100), nullable=True)
    physical_address: Mapped[str] = mapped_column(String(300), nullable=True)

    # Technical specifications
    kiosk_model: Mapped[str] = mapped_column(String(100), nullable=True)
    software_version: Mapped[str] = mapped_column(String(50), nullable=True)
    camera_specs: Mapped[str] = mapped_column(String(200), nullable=True)

    # Operational status
    kiosk_status: Mapped[str] = mapped_column(
        String(20), default="OFFLINE"
    )  # ONLINE, OFFLINE, MAINTENANCE, ERROR
    last_heartbeat: Mapped[date] = mapped_column(Date, nullable=True)
    uptime_percentage: Mapped[float] = mapped_column(Float(precision=2), default=0.0)

    # Capacity and usage
    daily_transaction_limit: Mapped[int] = mapped_column(Integer, default=100)
    current_daily_count: Mapped[int] = mapped_column(Integer, default=0)
    total_transactions_processed: Mapped[int] = mapped_column(Integer, default=0)

    # Maintenance
    last_maintenance: Mapped[date] = mapped_column(Date, nullable=True)
    next_scheduled_maintenance: Mapped[date] = mapped_column(Date, nullable=True)

    # Installation details
    installed_date: Mapped[date] = mapped_column(Date, nullable=False)
    installed_by_org: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    sessions = relationship("KioskSession", back_populates="kiosk")
    transactions = relationship("Transaction", back_populates="kiosk")
    verification_logs = relationship("VerificationLog", back_populates="kiosk")


class Supervisor(db.Model):
    """Field supervisors with verification permissions and on-site responsibilities"""

    __tablename__ = "supervisors"

    supervisor_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Personal information
    supervisor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supervisor_email: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True
    )
    employee_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Organization details
    organization_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("organizations.org_id")
    )
    position_title: Mapped[str] = mapped_column(String(100), nullable=False)
    clearance_level: Mapped[int] = mapped_column(
        Integer, default=2
    )  # 1-5 clearance levels (supervisors start at 2)

    # Permissions (limited compared to admins)
    can_verify_clients: Mapped[bool] = mapped_column(default=True)
    can_suspend_programs: Mapped[bool] = mapped_column(
        default=False
    )  # Only for specific cases
    can_access_logs: Mapped[bool] = mapped_column(default=True)
    can_emergency_override: Mapped[bool] = mapped_column(
        default=False
    )  # Emergency only

    # Geographic authorization
    authorized_area_codes: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # JSON array - limited to assigned areas
    current_assignment_location: Mapped[str] = mapped_column(String(100), nullable=True)

    # Status and activity
    supervisor_status: Mapped[str] = mapped_column(
        String(20), default="ACTIVE"
    )  # ACTIVE, SUSPENDED, TERMINATED
    last_login: Mapped[date] = mapped_column(Date, nullable=True)
    total_verifications_performed: Mapped[int] = mapped_column(Integer, default=0)

    # Employment details
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    contract_expiration: Mapped[date] = mapped_column(Date, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="supervisors")


class AlertLog(db.Model):
    """System alerts and notifications"""

    __tablename__ = "alert_logs"

    alert_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Alert classification
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # SECURITY, SYSTEM, VIOLATION, MAINTENANCE
    alert_severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # LOW, MEDIUM, HIGH, CRITICAL
    alert_category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # FRAUD_DETECTION, SYSTEM_ERROR, etc.

    # Alert content
    alert_title: Mapped[str] = mapped_column(String(200), nullable=False)
    alert_description: Mapped[str] = mapped_column(String(1000), nullable=False)
    alert_data: Mapped[str] = mapped_column(
        String(2000), nullable=True
    )  # JSON data related to alert

    # Source information
    source_system: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # KIOSK, VERIFICATION, ADMIN, etc.
    source_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # ID of the source entity
    affected_user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    affected_program_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Geographic information
    alert_location: Mapped[str] = mapped_column(String(100), nullable=True)
    area_code: Mapped[str] = mapped_column(String(50), nullable=True)

    # Timing
    alert_timestamp: Mapped[date] = mapped_column(Date, nullable=False)
    alert_expiry: Mapped[date] = mapped_column(Date, nullable=True)

    # Status and handling
    alert_status: Mapped[str] = mapped_column(
        String(20), default="OPEN"
    )  # OPEN, ACKNOWLEDGED, RESOLVED, DISMISSED
    acknowledged_by: Mapped[str] = mapped_column(String(255), nullable=True)
    acknowledged_at: Mapped[date] = mapped_column(Date, nullable=True)
    resolved_by: Mapped[str] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[date] = mapped_column(Date, nullable=True)
    resolution_notes: Mapped[str] = mapped_column(String(1000), nullable=True)

    # Escalation
    escalated: Mapped[bool] = mapped_column(default=False)
    escalated_to: Mapped[str] = mapped_column(String(255), nullable=True)
    escalation_reason: Mapped[str] = mapped_column(String(500), nullable=True)


class SystemConfig(db.Model):
    """Global system settings and configuration"""

    __tablename__ = "system_config"

    config_key: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Configuration value and metadata
    config_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    config_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # STRING, INTEGER, FLOAT, BOOLEAN, JSON
    config_description: Mapped[str] = mapped_column(String(500), nullable=True)

    # Configuration categories
    config_category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # SECURITY, LIMITS, AI, KIOSK, etc.
    config_subcategory: Mapped[str] = mapped_column(String(100), nullable=True)

    # Access control
    requires_admin: Mapped[bool] = mapped_column(default=True)
    requires_restart: Mapped[bool] = mapped_column(default=False)
    is_sensitive: Mapped[bool] = mapped_column(default=False)  # Hide value in logs/UI

    # Validation
    min_value: Mapped[str] = mapped_column(String(100), nullable=True)
    max_value: Mapped[str] = mapped_column(String(100), nullable=True)
    allowed_values: Mapped[str] = mapped_column(
        String(1000), nullable=True
    )  # JSON array for enum values
    validation_regex: Mapped[str] = mapped_column(String(200), nullable=True)

    # Change tracking
    default_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    last_modified_by: Mapped[str] = mapped_column(String(255), nullable=True)
    last_modified_at: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    # Environment specific
    environment: Mapped[str] = mapped_column(
        String(20), default="ALL"
    )  # ALL, DEV, TEST, PROD
    version_introduced: Mapped[str] = mapped_column(String(20), nullable=True)
