from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.admin import admin_bp
from .blueprints.client import client_bp
from .blueprints.employees import employees_bp
from .blueprints.programs import programs_bp
from .blueprints.tokens import tokens_bp
from .blueprints.verification import verification_bp
from .blueprints.public_pool_tokens import public_pool_tokens_bp
from .blueprints.kiosk_sessions import kiosk_sessions_bp
from .blueprints.organizations import organizations_bp
from .blueprints.wallets import wallets_bp
from .blueprints.transactions import transactions_bp
from .blueprints.kiosks import kiosks_bp
from .blueprints.supervisors import supervisors_bp
from .blueprints.alert_logs import alert_logs_bp
from .blueprints.system_config import system_config_bp
from .blueprints.fakedata import fakedata_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = "/static/swagger.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "landlink_db"}
)


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Import and register blueprints
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(programs_bp, url_prefix="/programs")
    app.register_blueprint(tokens_bp, url_prefix="/tokens")
    app.register_blueprint(verification_bp, url_prefix="/verification")
    app.register_blueprint(public_pool_tokens_bp, url_prefix="/public-pool-tokens")
    app.register_blueprint(kiosk_sessions_bp, url_prefix="/kiosk-sessions")
    app.register_blueprint(organizations_bp, url_prefix="/organizations")
    app.register_blueprint(wallets_bp, url_prefix="/wallets")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(kiosks_bp, url_prefix="/kiosks")
    app.register_blueprint(supervisors_bp, url_prefix="/supervisors")
    app.register_blueprint(alert_logs_bp, url_prefix="/alert-logs")
    app.register_blueprint(system_config_bp, url_prefix="/system-config")
    app.register_blueprint(fakedata_bp, url_prefix="/fakedata")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
