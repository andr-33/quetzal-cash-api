from flask import Flask
from app.config import Config
from app.balances.routes import balances_bp
from app.transactions.routes import transactions_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(balances_bp)
    app.register_blueprint(transactions_bp)

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(_e):
        return {"error": "Not found"}, 404

    return app