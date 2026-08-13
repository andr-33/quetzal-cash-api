from flask import Blueprint, request, jsonify
from app.transactions import controllers

transactions_bp = Blueprint('transactions', __name__, url_prefix="/api/transactions")

@transactions_bp.route("", methods=["GET"])
def list_transactions():
    month_filter = request.args.get("month")
    transactions = controllers.list_transactions(month_filter)
    return jsonify(transactions), 200

@transactions_bp.route("", methods=["POST"])
def create_transaction():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Cuerpo JSON requerido"}), 400

    created, error = controllers.create_income_or_expense(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(created), 201

@transactions_bp.route("/transfer", methods=["POST"])
def create_transfer():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Cuerpo JSON requerido"}), 400

    transfer, error = controllers.create_transfer(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(transfer), 201

@transactions_bp.route("/metrics", methods=["GET"])
def get_metrics():
    month_filter = request.args.get("month")
    metrics = controllers.get_metrics(month_filter)
    return jsonify(metrics), 200

@transactions_bp.route("/<tx_id>", methods=["PUT", "PATCH"])
def update_transaction(tx_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Cuerpo JSON requerido"}), 400

    updated, error = controllers.update_transaction(tx_id, data)
    if error:
        status_code = 404 if error == "Movimiento no encontrado" else 400
        return jsonify({"error": error}), status_code

    return jsonify(updated), 200

@transactions_bp.route("/<tx_id>", methods=["DELETE"])
def delete_transaction(tx_id):
    success, error = controllers.delete_transaction(tx_id)
    if not success:
        status_code = 404 if error == "Movimiento no encontrado" else 400
        return jsonify({"error": error}), status_code

    return jsonify({"message": "Movimiento eliminado exitosamente"}), 200
