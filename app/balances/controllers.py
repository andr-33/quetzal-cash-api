from app.balances import repository

def list_balances()-> list[dict]:
    return repository.list_all_balances()


    