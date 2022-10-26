import functools
from datetime import date
from typing import Dict, List, Union, Tuple

from backend.models import (
    Transaction,
    TransactionRow,
    TransactionState,
    TransactionType,
)
from backend.models.interfaces import Database


def transactions(db: Database, user_id: int) -> List[TransactionRow]:
    """
    Returns all transactions of a user.
    """
    return [
        transaction
        for transaction in db.scan("transactions")
        if transaction.user_id == user_id
    ]


def transaction(db, user_id, transaction_id) -> TransactionRow:
    """
    Returns a given transaction of the user
    """
    transaction = db.get("transactions", transaction_id)
    return transaction if transaction and transaction.user_id == user_id else None


def create_transaction(db, user_id, transaction: Transaction) -> TransactionRow:
    """
    Creates a new transaction (adds an ID) and returns it.
    """
    if transaction.type in (TransactionType.DEPOSIT, TransactionType.REFUND):
        initial_state = TransactionState.PENDING
    elif transaction.type == TransactionType.SCHEDULED_WITHDRAWAL:
        initial_state = TransactionState.SCHEDULED
    else:
        raise ValueError(f"Invalid transaction type {transaction.type}")
    transaction_row = TransactionRow(
        user_id=user_id, **transaction.dict(), state=initial_state
    )
    return db.put("transactions", transaction_row)


def compute_balance_without_future_transactions(
    transactions: List[TransactionRow],
) -> float:
    """
    Computes the "current" balance, i.e. the amount of money available without considering any future
    withdrawal.
    :param transactions: list of a user's transactions
    :return: the value of the current balance (float)
    """

    def get_transaction_contribution(
        tr_type: TransactionType, tr_state: TransactionState, tr_amount: float
    ) -> float:
        """
        Meant for the further "functools.reduce" call.
        It contains all the business rules describing how each transaction contributes to the balance,
        based on its "type" and "state".
        """
        rules = {
            TransactionType.DEPOSIT: {TransactionState.COMPLETED: 1.0},
            TransactionType.REFUND: {
                TransactionState.PENDING: -1.0,
                TransactionState.COMPLETED: -1.0,
            },
            TransactionType.SCHEDULED_WITHDRAWAL: {TransactionState.COMPLETED: -1.0},
        }

        try:
            return rules[tr_type][tr_state] * tr_amount
        except KeyError:
            return 0.0

    def transaction_amount_acc(
        current_accumulated_amount: float, transaction: TransactionRow
    ) -> float:
        return current_accumulated_amount + get_transaction_contribution(
            transaction.type, transaction.state, transaction.amount
        )

    balance = functools.reduce(transaction_amount_acc, transactions, 0.0)

    return balance


def compute_balance(
    current_balance: float, transactions: List[TransactionRow]
) -> Tuple[float, List[Dict[str, Union[int, float, date]]]]:
    """
    Computes the distribution of the current balance (given by compute_balance_without_future_transactions)
    over the upcoming withdrawals.
    :param current_balance: The balance without upcoming withdrawals
    :param transactions: a user's transaction list
    :return: Tuple containing
             1. the final balance, i.e. after the amount of each upcoming withdrawal has been withdrawn from
                the current balance
             2. the list of each upcoming witdrawal (dict) along with details on how the current balance
                covers each withdrawal
    """

    # Ensure only upcoming withdrawals are considered in the computation and ensure they
    # are handled in a chronological order
    uncompleted_scheduled_withdrawals = sorted(
        (
            tr
            for tr in transactions
            if tr.type == TransactionType.SCHEDULED_WITHDRAWAL
            and tr.state == TransactionState.SCHEDULED
        ),
        key=lambda tr: tr.date,
    )

    withdrawal_states: List[Dict[str, Union[int, float, date]]] = []

    for withdrawal in uncompleted_scheduled_withdrawals:
        withdrawal_states.append(
            {
                "withdrawal_amount": withdrawal.amount,
                "amount_covered": min(withdrawal.amount, current_balance),
                "percent_coverage_with_current_balance": round(
                    min(current_balance / withdrawal.amount, 1.0) * 100.0
                ),
                "scheduled_date": withdrawal.date,
            }
        )
        current_balance = max(0.0, current_balance - withdrawal.amount)

    return current_balance, withdrawal_states
