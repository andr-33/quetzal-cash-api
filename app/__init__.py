from flask import Flask
from app.config import Config
from app.balances.routes import balances_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(balances_bp, url_prefix="/api/balances")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(_e):
        return {"error": "Not found"}, 404

    return app