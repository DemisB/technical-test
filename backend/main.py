from typing import List

from fastapi import FastAPI, HTTPException

from backend.db import InMemoryDB
from backend.logic import transactions
from backend.models import Transaction, TransactionRow, UserBalanceAPIResponse

app = FastAPI()

db = InMemoryDB()


@app.get("/")
async def root():
    """Simple endpoint to test if the server is up and running"""
    return {"message": "Hello World"}


@app.get("/users/{user_id}/transactions")
async def get_transactions(user_id: int) -> List[TransactionRow]:
    """Returns all transactions for a user."""
    return transactions.transactions(db, user_id)


@app.get("/users/{user_id}/transactions/balance", response_model=UserBalanceAPIResponse)
async def get_balance(user_id: int) -> UserBalanceAPIResponse:
    """Computes the balance of payments for a user subscription."""
    user_transactions = transactions.transactions(db, user_id)
    current_balance = transactions.compute_balance_without_future_transactions(user_transactions)
    final_balance, upcoming_withdrawals = transactions.compute_balance(current_balance, user_transactions)

    return UserBalanceAPIResponse(balance=final_balance,
                                  upcoming_withdrawals=upcoming_withdrawals)


@app.get("/users/{user_id}/transactions/{transaction_id}")
async def get_transaction(user_id: int, transaction_id: int) -> TransactionRow:
    """Returns a given transaction of the user."""
    transaction = transactions.transaction(db, user_id, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/users/{user_id}/transactions")
async def create_transaction(user_id: int, transaction: Transaction) -> TransactionRow:
    """Adds a new transaction to the list of user transactions."""
    return transactions.create_transaction(db, user_id, transaction)
