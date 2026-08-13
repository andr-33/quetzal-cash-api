import gspread
from datetime import datetime, timezone
from flask import current_app as app
from app.extensions import get_sheets_client

HEADERS = ["id", "type", "amount", "category", "targetCategory", "date", "comment", "createdAt"]

def _get_worksheet():
    client = get_sheets_client(app.config)
    spreadsheet = client.open_by_key(app.config["GOOGLE_SHEET_ID"])
    try:
        return spreadsheet.worksheet("transactions")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="transactions", rows="1000", cols="10")
        worksheet.append_row(HEADERS)
        return worksheet

def _row_to_dict(row):
    target_cat = row.get("targetCategory")
    target_cat_val = str(target_cat).strip() if target_cat else None
    if target_cat_val == "":
        target_cat_val = None

    try:
        amount_val = float(row.get("amount", 0))
    except (ValueError, TypeError):
        amount_val = 0.0

    return {
        "id": str(row.get("id", "")),
        "type": str(row.get("type", "")),
        "amount": amount_val,
        "category": str(row.get("category", "")),
        "targetCategory": target_cat_val,
        "date": str(row.get("date", "")),
        "comment": str(row.get("comment", "")),
        "createdAt": str(row.get("createdAt", ""))
    }

def list_all_transactions() -> list[dict]:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()
    return [_row_to_dict(row) for row in rows]

def find_row_index_by_id(rows: list[dict], tx_id: str):
    target_id = str(tx_id).strip()
    for idx, row in enumerate(rows):
        if str(row.get("id")).strip() == target_id:
            return idx + 2, row  # Row 1 is header, data starts at row 2
    return None, None

def get_transaction_by_id(tx_id: str) -> dict | None:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()
    _row_idx, row = find_row_index_by_id(rows, tx_id)
    if row is None:
        return None
    return _row_to_dict(row)

def create_transaction(tx: dict) -> dict:
    worksheet = _get_worksheet()
    row_values = [
        tx.get("id", ""),
        tx.get("type", ""),
        tx.get("amount", 0),
        tx.get("category", ""),
        tx.get("targetCategory") or "",
        tx.get("date", ""),
        tx.get("comment", ""),
        tx.get("createdAt", "")
    ]
    worksheet.append_row(row_values)
    return tx

def update_transaction(tx_id: str, updated_fields: dict) -> dict | None:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()

    target_row_idx, target_row = find_row_index_by_id(rows, tx_id)
    if not target_row_idx:
        return None

    current_dict = _row_to_dict(target_row)
    merged_dict = {**current_dict, **updated_fields}

    headers = [str(h) for h in worksheet.row_values(1)]
    if not headers or len(headers) < len(HEADERS):
        headers = HEADERS

    for key, val in updated_fields.items():
        if key in headers:
            col_idx = headers.index(key) + 1
            cell_val = "" if val is None else val
            worksheet.update_cell(target_row_idx, col_idx, cell_val)

    return merged_dict

def delete_transaction(tx_id: str) -> bool:
    worksheet = _get_worksheet()
    rows = worksheet.get_all_records()

    target_row_idx, _target_row = find_row_index_by_id(rows, tx_id)
    if not target_row_idx:
        return False

    worksheet.delete_rows(target_row_idx)
    return True
