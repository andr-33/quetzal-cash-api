import uuid
from datetime import datetime, timezone
from app.balances import repository as balances_repo
from app.transactions import repository as tx_repo

VALID_CATEGORIES = {"caja", "piso", "inversion", "ahorro"}
VALID_TYPES = {"income", "expense", "transfer"}

def _apply_balance_impact(tx: dict, undo: bool = False):
    multiplier = -1 if undo else 1
    tx_type = tx.get("type")
    try:
        amt = float(tx.get("amount", 0))
    except (ValueError, TypeError):
        amt = 0.0

    category = tx.get("category")
    target_category = tx.get("targetCategory")

    if tx_type == "income" and category:
        balances_repo.adjust_balance_by_category(category, amt * multiplier)
    elif tx_type == "expense" and category:
        balances_repo.adjust_balance_by_category(category, -amt * multiplier)
    elif tx_type == "transfer" and category and target_category:
        balances_repo.adjust_balance_by_category(category, -amt * multiplier)
        balances_repo.adjust_balance_by_category(target_category, amt * multiplier)

def list_transactions(month_filter: str | None = None) -> list[dict]:
    all_txs = tx_repo.list_all_transactions()
    
    # Sort descending by date and createdAt
    sorted_txs = sorted(
        all_txs,
        key=lambda t: (t.get("date", ""), t.get("createdAt", "")),
        reverse=True
    )

    if not month_filter or month_filter.strip().lower() == "all":
        return sorted_txs

    target_month = month_filter.strip()
    return [t for t in sorted_txs if t.get("date", "").startswith(target_month)]

def create_income_or_expense(data: dict) -> tuple[dict | None, str | None]:
    tx_type = data.get("type")
    if tx_type not in {"income", "expense"}:
        return None, "El tipo debe ser 'income' o 'expense'"

    category = str(data.get("category", "")).strip().lower()
    if category not in VALID_CATEGORIES:
        return None, f"La categoría debe ser una de: {', '.join(sorted(VALID_CATEGORIES))}"

    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return None, "El monto debe ser un número positivo"
    except (ValueError, TypeError):
        return None, "El monto debe ser un número válido"

    date_str = str(data.get("date", "")).strip()
    if not date_str:
        return None, "La fecha es requerida"

    comment = str(data.get("comment", "")).strip()

    new_tx = {
        "id": f"tx-{int(datetime.now(timezone.utc).timestamp()*1000)}-{uuid.uuid4().hex[:6]}",
        "type": tx_type,
        "amount": round(amount, 2),
        "category": category,
        "targetCategory": None,
        "date": date_str,
        "comment": comment,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    created = tx_repo.create_transaction(new_tx)
    _apply_balance_impact(created, undo=False)
    return created, None

def create_transfer(data: dict) -> tuple[dict | None, str | None]:
    from_cat = str(data.get("fromCategory", "")).strip().lower()
    to_cat = str(data.get("toCategory", "")).strip().lower()

    if from_cat not in VALID_CATEGORIES or to_cat not in VALID_CATEGORIES:
        return None, f"Las categorías deben ser de: {', '.join(sorted(VALID_CATEGORIES))}"

    if from_cat == to_cat:
        return None, "La cuenta de origen y destino deben ser distintas"

    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return None, "El monto debe ser un número positivo"
    except (ValueError, TypeError):
        return None, "El monto debe ser un número válido"

    date_str = str(data.get("date", "")).strip()
    if not date_str:
        return None, "La fecha es requerida"

    comment = str(data.get("comment", "")).strip()
    if not comment:
        comment = f"Traspaso de {from_cat} a {to_cat}"

    transfer_tx = {
        "id": f"tx-{int(datetime.now(timezone.utc).timestamp()*1000)}-{uuid.uuid4().hex[:6]}",
        "type": "transfer",
        "amount": round(amount, 2),
        "category": from_cat,
        "targetCategory": to_cat,
        "date": date_str,
        "comment": comment,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    created = tx_repo.create_transaction(transfer_tx)
    _apply_balance_impact(created, undo=False)
    return created, None

def update_transaction(tx_id: str, updated_fields: dict) -> tuple[dict | None, str | None]:
    existing = tx_repo.get_transaction_by_id(tx_id)
    if not existing:
        return None, "Movimiento no encontrado"

    _apply_balance_impact(existing, undo=True)

    updated = tx_repo.update_transaction(tx_id, updated_fields)
    if not updated:
        # Re-apply if failed
        _apply_balance_impact(existing, undo=False)
        return None, "Error al actualizar movimiento"

    _apply_balance_impact(updated, undo=False)
    return updated, None

def delete_transaction(tx_id: str) -> tuple[bool, str | None]:
    existing = tx_repo.get_transaction_by_id(tx_id)
    if not existing:
        return False, "Movimiento no encontrado"

    _apply_balance_impact(existing, undo=True)
    deleted = tx_repo.delete_transaction(tx_id)
    if not deleted:
        _apply_balance_impact(existing, undo=False)
        return False, "Error al eliminar movimiento"

    return True, None

def get_metrics(month_filter: str | None = None) -> dict:
    txs = list_transactions(month_filter)

    total_income = round(sum(t["amount"] for t in txs if t.get("type") == "income"), 2)
    total_expense = round(sum(t["amount"] for t in txs if t.get("type") == "expense"), 2)

    category_breakdown = {
        cat: {"income": 0.0, "expense": 0.0} for cat in ["caja", "piso", "inversion", "ahorro"]
    }

    for tx in txs:
        cat = tx.get("category")
        t_type = tx.get("type")
        amt = float(tx.get("amount", 0))
        if cat in category_breakdown:
            if t_type == "income":
                category_breakdown[cat]["income"] = round(category_breakdown[cat]["income"] + amt, 2)
            elif t_type == "expense":
                category_breakdown[cat]["expense"] = round(category_breakdown[cat]["expense"] + amt, 2)

    return {
        "totalIncome": total_income,
        "totalExpense": total_expense,
        "netBalance": round(total_income - total_expense, 2),
        "categoryBreakdown": category_breakdown
    }
