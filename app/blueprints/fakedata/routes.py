# Fakedata routes
from flask import jsonify
from . import fakedata_bp
from app.models import (
    db,
    Admin,
    Client,
    Supervisor,
    Employee,
    Wallet,
    Transaction,
    Token,
    PublicPoolToken,
    Organization,
    Program,
    Kiosk,
    KioskSession,
    VerificationLog,
    AlertLog,
    SystemConfig,
)
from faker import Faker
from werkzeug.security import generate_password_hash
import random
import uuid
from datetime import date


@fakedata_bp.route("/seed-database", methods=["POST"])
def seed_database():
    """Generate realistic fake data for testing and development"""

    # Clear existing data (optional - be careful in production!)
    # Uncomment these lines if you want to clear existing data first
    # db.session.query(Admin).delete()
    # db.session.query(Client).delete()
    # db.session.query(Employee).delete()
    # db.session.query(Supervisor).delete()
    # db.session.commit()

    faker = Faker()

    # Define area codes used throughout the seeding
    area_codes = ["NY001", "CA002", "TX003", "FL004", "WA005"]

    # Create Admins
    admins = []
    for i in range(3):
        admin = Admin()
        admin.admin_id = str(uuid.uuid4())
        admin.admin_username = faker.unique.user_name()
        admin.hashed_password = generate_password_hash("AdminPassword123!")
        admin.admin_email = faker.unique.email()
        admin.admin_role = random.choice(["CEO", "ADMIN", "SECURITY_ADMIN"])
        admin.clearance_level = random.randint(3, 5)
        admin.created_at = date.today()
        admin.is_active = True
        admin.notes = f"Test admin created by faker - {faker.sentence()}"

        admins.append(admin)
        db.session.add(admin)

    # Create Employees
    employees = []
    departments = ["IT", "Security", "Operations", "Finance", "HR"]
    for i in range(10):
        employee = Employee()
        employee.employee_id = str(uuid.uuid4())
        employee.employee_username = faker.unique.user_name()
        employee.hashed_password = generate_password_hash("Employee123!")
        employee.employee_email = faker.unique.email()
        employee.employee_role = random.choice(["EMPLOYEE", "SENIOR_EMPLOYEE", "LEAD"])
        employee.department = random.choice(departments)
        employee.login_location_IP = faker.random_int(min=1000000, max=9999999)
        employee.created_at = date.today()
        employee.is_active = random.choice([True, True, True, False])  # Mostly active

        employees.append(employee)
        db.session.add(employee)

    # Create Organizations first (supervisors will reference these)
    organizations = []
    org_types = ["NGO", "GOVERNMENT", "PRIVATE", "INTERNATIONAL"]
    for i in range(5):
        organization = Organization()
        organization.org_id = str(uuid.uuid4())
        organization.organization_name = faker.company()
        organization.organization_type = random.choice(org_types)
        organization.authorized_regions = (
            f'["{random.choice(area_codes)}", "{random.choice(area_codes)}"]'
        )
        organization.contact_email = faker.email()
        organization.emergency_contact = faker.phone_number()
        organization.registered_at = date.today()
        if random.choice([True, False]):
            organization.last_access = date.today()

        organizations.append(organization)
        db.session.add(organization)

    # Create Supervisors (after organizations exist)
    supervisors = []
    position_titles = [
        "Field Supervisor",
        "Regional Manager",
        "Site Coordinator",
        "Operations Lead",
        "Program Director",
    ]
    for i in range(5):
        supervisor = Supervisor()
        supervisor.supervisor_id = str(uuid.uuid4())
        supervisor.supervisor_name = faker.name()
        supervisor.supervisor_email = faker.unique.email()
        supervisor.employee_id = str(faker.random_int(min=1000, max=9999))
        supervisor.organization_id = random.choice(
            organizations
        ).org_id  # Reference existing organization
        supervisor.position_title = random.choice(position_titles)  # Required field
        supervisor.clearance_level = random.randint(1, 3)
        supervisor.can_verify_clients = True
        supervisor.can_suspend_programs = random.choice([True, False])
        supervisor.can_access_logs = True
        supervisor.can_emergency_override = random.choice([True, False])
        supervisor.authorized_area_codes = (
            f'["{random.choice(area_codes)}", "{random.choice(area_codes)}"]'
        )
        supervisor.supervisor_status = "ACTIVE"
        supervisor.hire_date = date.today()  # Required field

        supervisors.append(supervisor)
        db.session.add(supervisor)

    # Create Clients
    clients = []
    for i in range(25):
        client = Client()
        client.client_id = str(uuid.uuid4())
        client.client_name = faker.name()
        client.client_email = faker.email() if random.choice([True, False]) else ""
        client.client_phone = (
            faker.phone_number() if random.choice([True, False]) else ""
        )
        client.area_code = random.choice(area_codes)
        client.created_at = date.today()
        client.is_active = True
        client.login_location_IP = faker.random_int(min=1000000, max=9999999)

        clients.append(client)
        db.session.add(client)

    # Create Programs
    programs = []
    for i in range(8):
        program = Program()
        program.hashed_program_id = str(uuid.uuid4())
        program.region = faker.state()
        program.estimated_beneficiaries = random.randint(100, 5000)
        program.area_code = random.choice(area_codes)
        program.created_at = date.today()
        program.expiration_deadline = date.today()  # You might want to adjust this
        program.program_status = random.choice(["ACTIVE", "SUSPENDED"])
        program.violation_count = random.randint(0, 3)

        programs.append(program)
        db.session.add(program)

    # Create Kiosks (needed for sessions and verification logs)
    kiosks = []
    kiosk_statuses = ["ONLINE", "OFFLINE", "MAINTENANCE", "ERROR"]
    for i in range(15):  # 15 kiosks across different areas
        kiosk = Kiosk()
        kiosk.kiosk_id = str(uuid.uuid4())
        kiosk.kiosk_location = f"{faker.city()} Relief Center"
        kiosk.area_code = random.choice(area_codes)
        kiosk.gps_coordinates = f"{faker.latitude()}, {faker.longitude()}"
        kiosk.physical_address = faker.address()
        kiosk.kiosk_model = random.choice(
            ["AidStation-Pro", "HelpPoint-2000", "ReliefKiosk-X1"]
        )
        kiosk.software_version = (
            f"v{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}"
        )
        kiosk.camera_specs = random.choice(["HD-1080p", "4K-Ultra", "Biometric-Pro"])
        kiosk.kiosk_status = random.choice(kiosk_statuses)
        if kiosk.kiosk_status == "ONLINE":
            kiosk.last_heartbeat = date.today()
        kiosk.uptime_percentage = round(random.uniform(85.0, 99.9), 2)
        kiosk.daily_transaction_limit = random.randint(50, 200)
        kiosk.current_daily_count = random.randint(0, 50)
        kiosk.total_transactions_processed = random.randint(100, 5000)
        kiosk.installed_date = date.today()
        kiosk.installed_by_org = random.choice(organizations).org_id

        kiosks.append(kiosk)
        db.session.add(kiosk)

    # Create Wallets
    wallets = []
    for client in clients[:15]:  # Create wallets for some clients
        wallet = Wallet()
        wallet.wallet_id = str(uuid.uuid4())
        wallet.client_id = client.client_id
        wallet.wallet_balance = round(random.uniform(0, 1000), 2)
        wallet.total_tokens_received = random.randint(5, 50)
        wallet.total_tokens_redeemed = random.randint(0, 30)
        wallet.wallet_hash = str(uuid.uuid4())
        wallet.created_at = date.today()
        if random.choice([True, False]):
            wallet.last_activity = date.today()
        wallet.wallet_status = random.choice(["ACTIVE", "SUSPENDED"])

        wallets.append(wallet)
        db.session.add(wallet)

    # Create Tokens
    tokens = []
    for i in range(100):
        token = Token()
        token.token_id = str(uuid.uuid4())
        token.client_id = random.choice(clients).client_id
        token.program_id = random.choice(programs).hashed_program_id
        token.token_amount = round(random.uniform(50, 500), 2)
        token.weekly_limit = round(random.uniform(25, 100), 2)
        token.weekly_redeemed = round(random.uniform(0, 50), 2)
        token.area_code = random.choice(area_codes)
        token.claim_status = random.choice(
            ["ACTIVE", "REDEEMED", "TRANSFERRED_TO_POOL"]
        )
        token.issued_at = date.today()
        if random.choice([True, False]):
            token.last_redemption = date.today()

        tokens.append(token)
        db.session.add(token)

    # Create Public Pool Tokens
    public_pool_tokens = []
    for i in range(200):
        pool_token = PublicPoolToken()
        pool_token.token_id = str(uuid.uuid4())
        pool_token.token_amount = round(random.uniform(25, 200), 2)
        pool_token.area_code = random.choice(area_codes)
        pool_token.pool_entry_date = date.today()
        pool_token.claim_status = random.choice(["AVAILABLE", "CLAIMED"])
        pool_token.original_program_id = random.choice(programs).hashed_program_id
        pool_token.transfer_reason = random.choice(["EXPIRED", "SUSPENDED"])
        if pool_token.claim_status == "CLAIMED":
            pool_token.claimed_by_user_id = random.choice(clients).client_id
            pool_token.claimed_at = date.today()

        public_pool_tokens.append(pool_token)
        db.session.add(pool_token)

    # Create Transactions
    transactions = []
    for i in range(30):
        transaction = Transaction()
        transaction.transaction_id = str(uuid.uuid4())
        transaction.wallet_id = random.choice(wallets).wallet_id
        if random.choice([True, False]):
            transaction.token_id = random.choice(tokens).token_id
        transaction.transaction_type = random.choice(
            ["REDEMPTION", "TRANSFER", "ISSUANCE"]
        )
        transaction.transaction_amount = round(random.uniform(10, 300), 2)
        transaction.transaction_status = random.choice(
            ["COMPLETED", "PENDING", "FAILED"]
        )
        transaction.transaction_hash = str(uuid.uuid4())
        transaction.transaction_location = faker.city()
        transaction.transaction_timestamp = date.today()
        if transaction.transaction_status == "COMPLETED":
            transaction.completed_at = date.today()
        transaction.retry_count = random.randint(0, 2)

        transactions.append(transaction)
        db.session.add(transaction)

    # Create Kiosk Sessions
    kiosk_sessions = []
    session_statuses = ["ACTIVE", "COMPLETED", "ABANDONED"]
    for i in range(30):  # 30 sessions across kiosks
        session = KioskSession()
        session.session_id = str(uuid.uuid4())
        session.kiosk_id = random.choice(kiosks).kiosk_id
        if random.choice([True, False]):
            session.hashed_user_id = random.choice(clients).client_id
        session.session_status = random.choice(session_statuses)
        session.identity_verified = random.choice([True, False])
        session.un_staff_present = random.choice([True, False])
        session.dual_photo_captured = random.choice([True, False])
        session.session_start = date.today()
        session.last_activity = date.today()
        if session.session_status in ["COMPLETED", "ABANDONED"]:
            session.session_end = date.today()

        kiosk_sessions.append(session)
        db.session.add(session)

    # Create Verification Logs
    verification_logs = []
    verification_statuses = ["SUCCESS", "FAILED", "FLAGGED"]
    for i in range(50):  # 50 verification attempts
        log = VerificationLog()
        if random.choice([True, False]):
            log.client_id = random.choice(clients).client_id
        log.program_id = random.choice(programs).hashed_program_id
        log.verification_status = random.choice(verification_statuses)
        log.ai_confidence_score = round(random.uniform(0.3, 0.99), 3)
        log.dual_verification_passed = random.choice([True, False])
        if log.verification_status == "FAILED":
            log.failure_reason = random.choice(
                [
                    "Low confidence score",
                    "Biometric mismatch",
                    "Document invalid",
                    "Geographic violation",
                ]
            )
        log.geographic_violation = random.choice([True, False])
        log.kiosk_location = random.choice(kiosks).kiosk_location
        log.kiosk_id = random.choice(kiosks).kiosk_id
        if random.choice([True, False]):
            log.supervisor_id = random.choice(supervisors).supervisor_id
        log.verification_timestamp = date.today()

        verification_logs.append(log)
        db.session.add(log)

    # Create Alert Logs
    alert_logs = []
    alert_types = ["SECURITY", "SYSTEM", "VIOLATION", "MAINTENANCE"]
    alert_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    alert_statuses = ["OPEN", "ACKNOWLEDGED", "RESOLVED", "DISMISSED"]

    for i in range(25):  # 25 system alerts
        alert = AlertLog()
        alert.alert_type = random.choice(alert_types)
        alert.alert_severity = random.choice(alert_severities)
        alert.alert_category = random.choice(
            [
                "FRAUD_DETECTION",
                "SYSTEM_ERROR",
                "BIOMETRIC_FAILURE",
                "NETWORK_ISSUE",
                "MAINTENANCE_DUE",
                "SUSPICIOUS_ACTIVITY",
            ]
        )
        alert.alert_title = f"{alert.alert_type}: {faker.sentence(nb_words=4)}"
        alert.alert_description = faker.text(max_nb_chars=200)
        alert.source_system = random.choice(
            ["KIOSK", "VERIFICATION", "ADMIN", "AI_SYSTEM"]
        )
        alert.source_id = (
            random.choice(kiosks).kiosk_id
            if alert.source_system == "KIOSK"
            else str(uuid.uuid4())
        )
        if random.choice([True, False]):
            alert.affected_user_id = random.choice(clients).client_id
        if random.choice([True, False]):
            alert.affected_program_id = random.choice(programs).hashed_program_id
        if random.choice([True, False]):
            alert.alert_location = faker.city()
        if random.choice([True, False]):
            alert.area_code = random.choice(area_codes)
        alert.alert_timestamp = date.today()
        alert.alert_status = random.choice(alert_statuses)

        if alert.alert_status in ["ACKNOWLEDGED", "RESOLVED"]:
            alert.acknowledged_by = random.choice(admins).admin_id
            alert.acknowledged_at = date.today()

        if alert.alert_status == "RESOLVED":
            alert.resolved_by = random.choice(admins).admin_id
            alert.resolved_at = date.today()
            alert.resolution_notes = faker.sentence()

        alert_logs.append(alert)
        db.session.add(alert)

    # Create System Config (safe test configs only)
    system_configs = []
    safe_configs = [
        {
            "key": "TEST_MODE_ENABLED",
            "value": "true",
            "type": "BOOLEAN",
            "category": "TESTING",
            "description": "Enable test mode for development",
        },
        {
            "key": "FAKE_DATA_VERSION",
            "value": "v1.0",
            "type": "STRING",
            "category": "TESTING",
            "description": "Version of fake data generation",
        },
        {
            "key": "MAX_FAKE_TRANSACTIONS_PER_DAY",
            "value": "1000",
            "type": "INTEGER",
            "category": "TESTING",
            "description": "Maximum fake transactions per day",
        },
        {
            "key": "DEVELOPMENT_AI_THRESHOLD",
            "value": "0.75",
            "type": "FLOAT",
            "category": "AI",
            "description": "AI confidence threshold for development",
        },
        {
            "key": "TEST_GEOGRAPHIC_CODES",
            "value": '["NY001", "CA002", "TX003", "FL004", "WA005"]',
            "type": "JSON",
            "category": "TESTING",
            "description": "Test area codes for development",
        },
    ]

    for config_data in safe_configs:
        config = SystemConfig()
        config.config_key = config_data["key"]
        config.config_value = config_data["value"]
        config.config_type = config_data["type"]
        config.config_description = config_data["description"]
        config.config_category = config_data["category"]
        config.requires_admin = True
        config.requires_restart = False
        config.is_sensitive = False
        config.default_value = config_data["value"]
        config.created_at = date.today()
        config.environment = "DEV"

        system_configs.append(config)
        db.session.add(config)

    try:
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Database seeded successfully!",
                    "data_created": {
                        "admins": len(admins),
                        "employees": len(employees),
                        "supervisors": len(supervisors),
                        "clients": len(clients),
                        "organizations": len(organizations),
                        "programs": len(programs),
                        "kiosks": len(kiosks),
                        "wallets": len(wallets),
                        "tokens": len(tokens),
                        "public_pool_tokens": len(public_pool_tokens),
                        "transactions": len(transactions),
                        "kiosk_sessions": len(kiosk_sessions),
                        "verification_logs": len(verification_logs),
                        "alert_logs": len(alert_logs),
                        "system_configs": len(system_configs),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to seed database: {str(e)}"}), 500
