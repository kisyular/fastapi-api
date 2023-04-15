import pytest
from app.calculation import (
    add,
    divide,
    multipy,
    subtract,
    BankAccount,
    InsufficcientFunds,
)


@pytest.mark.parametrize("num1, num2, expected", [(5, 7, 12), (4, 2, 6), (9, 8, 17)])
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected


@pytest.mark.parametrize("num1, num2, expected", [(5, 7, -2), (4, 2, 2), (9, 8, 1)])
def test_subtract(num1, num2, expected):
    assert subtract(num1, num2) == expected


@pytest.mark.parametrize("num1, num2, expected", [(5, 7, 35), (4, 2, 8), (9, 8, 72)])
def test_divide(num1, num2, expected):
    assert multipy(num1, num2) == expected


@pytest.mark.parametrize(
    "num1, num2, expected", [(5, 7, 0.7142857142857143), (4, 2, 2), (9, 8, 1.125)]
)
def test_multiply(num1, num2, expected):
    assert divide(num1, num2) == expected


@pytest.mark.parametrize("num1, num2", [(5, 0), (4, 0), (9, 0)])
def test_divide_by_zero(num1, num2):
    with pytest.raises(ZeroDivisionError):
        divide(num1, num2)


def test_default_amount():
    bank_account = BankAccount()
    assert bank_account.balance == 0


@pytest.mark.parametrize("starting_balance", [50, 100, 200])
def test_set_initial_amount(starting_balance):
    bank_account = BankAccount(starting_balance)
    assert bank_account.balance == starting_balance


@pytest.mark.parametrize("starting_balance", [50, 100, 200])
def test_withdraw(starting_balance):
    bank_account = BankAccount(starting_balance)
    bank_account.withdraw(20)
    assert bank_account.balance == starting_balance - 20


@pytest.mark.parametrize("starting_balance", [50, 100, 200])
def test_deposit(starting_balance):
    bank_account = BankAccount(starting_balance)
    bank_account.deposit(30)
    assert bank_account.balance == starting_balance + 30


@pytest.mark.parametrize("starting_balance", [50, 100, 200])
def test_collect_interest(starting_balance):
    bank_account = BankAccount(starting_balance)
    bank_account.collect_interest()
    assert bank_account.balance == starting_balance * 1.1


# ------------------------------------------------------------
@pytest.fixture
def zero_bank_account():
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(50)


def test_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_set_initial_amount(bank_account):
    assert bank_account.balance == 50


def test_withdraw(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30


def test_deposit(bank_account):
    bank_account.deposit(30)
    assert bank_account.balance == 80


def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert bank_account.balance == 50 * 1.1


@pytest.mark.parametrize(
    "deposited, withdrew, expected", [(200, 50, 150), (80, 20, 60), (45, 5, 40)]
)
def test_transactions(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected


def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficcientFunds):
        bank_account.withdraw(200)
