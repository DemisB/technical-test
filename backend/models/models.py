from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel


class TransactionType(str, Enum):
    DEPOSIT: str = "deposit"
    SCHEDULED_WITHDRAWAL: str = "scheduled_withdrawal"
    REFUND: str = "refund"


class TransactionState(str, Enum):
    SCHEDULED: str = "scheduled"
    PENDING: str = "pending"
    COMPLETED: str = "completed"
    FAILED: str = "failed"


class Row(BaseModel):
    id: int = 0  # id is overwritten by the database upon insertion


class User(BaseModel):
    name: str
    email: str


class UserRow(Row, User):
    pass


class Transaction(BaseModel):
    amount: float
    date: date
    type: TransactionType


class TransactionRow(Row, Transaction):
    user_id: int
    state: TransactionState


class WithdrawalCoverage(BaseModel):
    withdrawal_amount: float
    amount_covered: float
    percent_coverage_with_current_balance: int
    scheduled_date: date


class UserBalanceAPIResponse(BaseModel):
    balance: float
    upcoming_withdrawals: List[WithdrawalCoverage]
