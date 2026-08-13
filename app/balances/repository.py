import uuid
from datetime import datetime, timezone
from flask import current_app as app
from app.extensions import get_sheets_client

def _get_worksheet():
    client = get_sheets_client(app.config)
    spreadsheet = client.open_by_key(app.config["GOOGLE_SHEET_ID"])
    return spreadsheet.worksheet("balances")

def _row_to_dict(row):
    return {
        "id": row.get("id"),
        "category": row.get("category"),
        "amount": row.get("amount"),
        "updated_at": row.get("updated_at", "")
    }

def list_all_balances():
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()
    return [_row_to_dict(row) for row in rows]

def find_row_index_by_id(rows: list[dict], balance_id: str):
    for idx, row in enumerate(rows):
        if str(row.get("id")) == str(balance_id):
            return idx + 2, row  # Row 1 is header, data starts at row 2
    return None, None

def find_row_index_by_category(rows: list[dict], category: str):
    target_cat = str(category).strip().lower()
    for idx, row in enumerate(rows):
        if str(row.get("category")).strip().lower() == target_cat:
            return idx + 2, row
    return None, None

def update_balance_amount(balance_id: str, new_amount: float | int):
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()

    target_row_idx, target_row = find_row_index_by_id(rows, balance_id)
    if not target_row_idx:
        return None

    headers = [str(h) for h in worksheet.row_values(1)]

    amount_col = headers.index("amount") + 1 if "amount" in headers else 3
    updated_at_col = headers.index("updated_at") + 1 if "updated_at" in headers else 4

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    worksheet.update_cell(target_row_idx, amount_col, new_amount)
    worksheet.update_cell(target_row_idx, updated_at_col, updated_at)

    updated_row = dict(target_row)
    updated_row["amount"] = new_amount
    updated_row["updated_at"] = updated_at

    return _row_to_dict(updated_row)

def adjust_balance_by_category(category: str, delta: float):
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()

    target_row_idx, target_row = find_row_index_by_category(rows, category)
    if not target_row_idx:
        return None

    headers = [str(h) for h in worksheet.row_values(1)]
    amount_col = headers.index("amount") + 1 if "amount" in headers else 3
    updated_at_col = headers.index("updated_at") + 1 if "updated_at" in headers else 4

    try:
        current_amt = float(target_row.get("amount", 0))
    except (ValueError, TypeError):
        current_amt = 0.0

    new_amount = round(current_amt + delta, 2)
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    worksheet.update_cell(target_row_idx, amount_col, new_amount)
    worksheet.update_cell(target_row_idx, updated_at_col, updated_at)

    updated_row = dict(target_row)
    updated_row["amount"] = new_amount
    updated_row["updated_at"] = updated_at

    return _row_to_dict(updated_row)