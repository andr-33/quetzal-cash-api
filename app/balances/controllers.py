from app.balances import repository

def list_balances() -> list[dict]:
    return repository.list_all_balances()

def update_balance(balance_id: str, amount: float | int) -> dict | None:
    return repository.update_balance_amount(balance_id, amount)