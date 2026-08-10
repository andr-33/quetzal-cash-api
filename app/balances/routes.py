from flask import Blueprint, request, jsonify
from app.balances import controllers

balances_bp = Blueprint('balances', __name__)

@balances_bp.route("", methods=["GET"])
def list_balances():
    return jsonify(controllers.list_balances()), 200





