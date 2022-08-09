from fastapi import FastAPI, HTTPException

from backend.db import InMemoryDB
from backend.logic import transactions
from backend.models import Transaction

app = FastAPI()

db = InMemoryDB()


@app.get("/")
async def root():
    """Simple endpoint to test if the server is up and running"""
    return {"message": "Hello World"}


@app.get("/users/{user_id}/transactions")
async def get_transactions(user_id: int):
    """Returns all transactions for a user."""
    return transactions.transactions(db, user_id)


@app.get("/users/{user_id}/transactions/{transaction_id}")
async def get_transaction(user_id: int, transaction_id: int):
    """Returns a given transaction of the user."""
    transaction = transactions.transaction(db, user_id, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/users/{user_id}/transactions")
async def create_transaction(user_id: int, transaction: Transaction):
    """Adds a new transaction to the list of user transactions."""
    return transactions.create_transaction(db, user_id, transaction)


@app.get("/users/{user_id}/transactions/balance")
async def get_balance(user_id: int):  # pylint: disable=unused-argument
    """Computes the balance of payments for a user subscription."""
    # We expect you to write this function
    return None