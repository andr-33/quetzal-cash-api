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