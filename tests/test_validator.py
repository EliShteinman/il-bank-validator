# tests/test_validator.py

import pytest

from il_bank_validator import (InvalidBankAccountException,
                               validate_israeli_bank_account)

# Test cases based on examples from MASAV document effective May 2025
VALIDATION_TEST_CASES = [
    (10, 936, "07869660", True, "Leumi - Valid example from docs"),
    (10, 936, "07869661", False, "Leumi - Invalid, wrong check digit"),
    (12, 571, "41116", True, "Hapoalim - Valid example"),
    (12, 571, "41117", False, "Hapoalim - Invalid"),
    (4, 284, "50067", True, "Yahav - Valid example"),
    (4, 284, "50068", False, "Yahav - Invalid"),
    (11, 1, "000032018", True, "Discount - Valid example"),
    (11, 1, "000032019", False, "Discount - Invalid"),
    (20, 406, "160778", True, "Mizrahi - Valid example (branch adjustment)"),
    (20, 6, "160778", True, "Mizrahi - Valid example (branch < 401)"),
    (31, 1, "32018", True, "FIBI - Valid example"),
    (9, 1, "059121900", True, "Postal Bank - Valid example"),
    (22, 1, "700241017", True, "Citibank - Valid example"),
    (22, 1, "700241018", False, "Citibank - Invalid"),
    (18, 1, "123456771", True, "One Zero - Valid example"),
    (3, 1, "247652342", True, "Ash - Valid (doc example has a typo in sum)"),
    (3, 1, "247652341", False, "Ash - Invalid"),
    (47, 1, "700241014", True, "Global Remit - Valid example"),
    (35, 100, "1234593", True, "GROW - Valid example"),
    (15, 1, "123456771", True, "Ofek - Valid example"),
    (21, 1, "16632427", True, "Nima - Valid example"),
    (58, 1, "162144279", True, "Rewire - Valid example"),
    # Marking Isracard as xfail due to ambiguous documentation
    pytest.param(
        1,
        1,
        "6543213",
        True,
        "Isracard - Valid example",
        marks=pytest.mark.xfail(reason="Isracard algorithm in MASAV doc is ambiguous"),
    ),
    (69, 1, "123456771", True, "GMT - Valid example"),
    (79, 19, "012345637", True, "019 - Valid example"),
]


@pytest.mark.parametrize(
    "bank_code, branch_code, account_number, expected, description",
    VALIDATION_TEST_CASES,
)
def test_bank_account_validation(
    bank_code, branch_code, account_number, expected, description
):
    assert (
        validate_israeli_bank_account(bank_code, branch_code, account_number)
        is expected
    ), description


def test_no_validation_rule_banks():
    assert validate_israeli_bank_account(
        54, 123, "123456"
    ), "Bank of Jerusalem should be valid"
    assert validate_israeli_bank_account(39, 1, "123456"), "Indian Bank should be valid"
    assert validate_israeli_bank_account(13, 1, "12345"), "Bank Igud should be valid"


def test_invalid_input_types():
    with pytest.raises(InvalidBankAccountException, match="Invalid input types"):
        validate_israeli_bank_account("10", 936, "07869660")


def test_non_digit_account_number():
    with pytest.raises(
        InvalidBankAccountException, match="Account number must contain only digits"
    ):
        validate_israeli_bank_account(10, 936, "123-456")


def test_unsupported_bank_code():
    with pytest.raises(
        InvalidBankAccountException, match="Bank with code '99' is not supported"
    ):
        validate_israeli_bank_account(99, 123, "123456")
