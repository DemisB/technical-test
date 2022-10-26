from datetime import date

import pytest
from backend.models import TransactionRow
from backend.logic.transactions import compute_balance_without_future_transactions, compute_balance


@pytest.fixture
def transaction_list_1():
    transaction_list = [{'amount': '20', 'date': '2020-01-01', 'state': 'completed', 'type': 'deposit', "user_id": 42},
                        {'amount': '10', 'date': '2020-01-02', 'state': 'failed', 'type': 'deposit', "user_id": 42},
                        {'amount': '30', 'date': '2020-01-05', 'state': 'completed', 'type': 'deposit', "user_id": 42},
                        {'amount': '20', 'date': '2020-01-15', 'state': 'completed', 'type': 'scheduled_withdrawal', "user_id": 42},
                        {'amount': '15', 'date': '2020-01-16', 'state': 'completed', 'type': 'deposit', "user_id": 42},
                        {'amount': '10', 'date': '2020-01-17', 'state': 'completed', 'type': 'deposit', "user_id": 42},
                        {'amount': '10', 'date': '2020-01-17', 'state': 'completed', 'type': 'refund', "user_id": 42},
                        {'amount': '15', 'date': '2020-01-28', 'state': 'pending', 'type': 'deposit', "user_id": 42},
                        {'amount': '20', 'date': '2020-02-15', 'state': 'scheduled', 'type': 'scheduled_withdrawal', "user_id": 42},
                        {'amount': '20', 'date': '2020-03-15', 'state': 'scheduled', 'type': 'scheduled_withdrawal', "user_id": 42},
                        {'amount': '20', 'date': '2020-04-15', 'state': 'scheduled', 'type': 'scheduled_withdrawal', "user_id": 42},
                        {'amount': '20', 'date': '2020-05-15', 'state': 'scheduled', 'type': 'scheduled_withdrawal', "user_id": 42}]

    return [TransactionRow(**tr) for tr in transaction_list]


@pytest.fixture
def transaction_list_2():
    transaction_list = [{'amount': '40', 'date': '2020-01-01', 'state': 'completed', 'type': 'deposit', "user_id": 666},
                        {'amount': '10', 'date': '2020-01-15', 'state': 'pending', 'type': 'refund', "user_id": 666},
                        {'amount': '20', 'date': '2020-01-15', 'state': 'scheduled', 'type': 'scheduled_withdrawal', "user_id": 666}]

    return [TransactionRow(**tr) for tr in transaction_list]


def test_compute_balance_without_future_transactions_case_1(transaction_list_1):
    assert compute_balance_without_future_transactions(transaction_list_1) == 45.0


def test_compute_balance_case_1(transaction_list_1):
    final_balance, upcoming_withdrawals = compute_balance(45.0, transaction_list_1)

    expected_final_balance = 0.0
    expected_upcoming_withdrawals = [
        {
            "withdrawal_amount": 20.0,
            "amount_covered": 20.0,
            "percent_coverage_with_current_balance": 100,
            "scheduled_date": date.fromisoformat("2020-02-15")
        },
        {
            "withdrawal_amount": 20.0,
            "amount_covered": 20.0,
            "percent_coverage_with_current_balance": 100,
            "scheduled_date": date.fromisoformat("2020-03-15")
        },
        {
            "withdrawal_amount": 20.0,
            "amount_covered": 5.0,
            "percent_coverage_with_current_balance": 25,
            "scheduled_date": date.fromisoformat("2020-04-15")
        },
        {
            "withdrawal_amount": 20.0,
            "amount_covered": 0.0,
            "percent_coverage_with_current_balance": 0,
            "scheduled_date": date.fromisoformat("2020-05-15")
        },
    ]

    assert final_balance == expected_final_balance
    assert upcoming_withdrawals == expected_upcoming_withdrawals


def test_compute_balance_without_future_transactions_case_2(transaction_list_2):
    assert compute_balance_without_future_transactions(transaction_list_2) == 30.0


def test_compute_balance_case_2(transaction_list_2):
    final_balance, upcoming_withdrawals = compute_balance(30.0, transaction_list_2)

    expected_final_balance = 10.0
    expected_upcoming_withdrawals = [
        {
            "withdrawal_amount": 20.0,
            "amount_covered": 20.0,
            "percent_coverage_with_current_balance": 100,
            "scheduled_date": date.fromisoformat("2020-01-15")
        }
    ]

    assert final_balance == expected_final_balance
    assert upcoming_withdrawals == expected_upcoming_withdrawals
