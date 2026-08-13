from flask import Blueprint, request, jsonify
from app.balances import controllers

balances_bp = Blueprint('balances', __name__, url_prefix="/api/balances")

@balances_bp.route("", methods=["GET"])
def list_balances():
    return jsonify(controllers.list_balances()), 200

@balances_bp.route("/<balance_id>", methods=["PUT", "PATCH"])
def update_balance(balance_id):
    data = request.get_json(silent=True)
    if not data or "amount" not in data:
        return jsonify({"error": "Field 'amount' is required"}), 400

    amount = data["amount"]
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        return jsonify({"error": "Field 'amount' must be a number"}), 400

    updated = controllers.update_balance(balance_id, amount)
    if not updated:
        return jsonify({"error": "Balance not found"}), 404

    return jsonify(updated), 200





