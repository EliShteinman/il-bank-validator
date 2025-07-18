# il_bank_validator/validator.py

from .exceptions import InvalidBankAccountException
from typing import List

# --- Helper Functions ---


def _calculate_weighted_sum_left_to_right(digits: str, weights: List[int]) -> int:
    """Calculates a weighted sum, applying weights from left to right."""
    total = 0
    for i, digit in enumerate(digits):
        if i < len(weights):
            total += int(digit) * weights[i]
    return total


def _calculate_weighted_sum_right_to_left(digits: str, weights: List[int]) -> int:
    """Calculates a weighted sum, applying weights from right to left."""
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i < len(weights):
            total += int(digit) * weights[i]
    return total


def _validate_mod11(
    full_number: str,
    weights: List[int],
    valid_remainders: List[int],
    right_to_left=False,
) -> bool:
    """Generic MOD 11 validation logic based on direction."""
    if not full_number.isdigit():
        return False

    calculator = (
        _calculate_weighted_sum_right_to_left
        if right_to_left
        else _calculate_weighted_sum_left_to_right
    )
    total = calculator(full_number, weights)
    return (total % 11) in valid_remainders


def _validate_mod97(
    branch_code: str, account_number: str, zero_pad_branch=True, no_pad_account=False
) -> bool:
    """Generic MOD 97 validation logic (ISO 7064 style)."""
    if not account_number.isdigit() or len(account_number) < 3:
        return False
    try:
        branch_str = branch_code.zfill(3) if zero_pad_branch else branch_code
        account_part = account_number[:-2]

        num_part_str = branch_str + account_part
        num_part_int = int(num_part_str)
        check_digits = int(account_number[-2:])

        # 98 is the basis for ISO 7064 MOD 97-10
        calculated_check_digits = 98 - (num_part_int % 97)

        # Handle the edge case where remainder is 1, which results in 97.
        if num_part_int % 97 == 1:
            return check_digits == 97

        return calculated_check_digits == check_digits
    except (ValueError, TypeError):
        return False


# --- Bank-Specific Validation Functions ---


def _validate_leumi(branch_code: str, account_number: str) -> bool:
    acc_norm = account_number.zfill(8)
    if not acc_norm.isdigit() or len(acc_norm) != 8:
        return False

    # Per doc example, calc is on all 3 branch digits + first 6 account digits.
    calc_str = branch_code.zfill(3) + acc_norm[:6]
    weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    base_sum = _calculate_weighted_sum_left_to_right(calc_str, weights)

    check_digits = int(acc_norm[-2:])
    constants = [128, 180, 330, 340]
    if acc_norm[4:6] not in ["00", "20", "23"]:
        constants.append(110)

    for const in constants:
        remainder = (base_sum + const) % 100
        calculated_check = 0 if remainder == 0 else 100 - remainder
        if calculated_check == check_digits:
            return True
    return False


def _validate_hapoalim(branch_code: str, account_number: str) -> bool:
    full_number = branch_code.zfill(3) + account_number.zfill(6)
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    return _validate_mod11(full_number, weights, [0, 2, 4, 6])


def _validate_yahav(branch_code: str, account_number: str) -> bool:
    full_number = branch_code.zfill(3) + account_number.zfill(6)
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    return _validate_mod11(full_number, weights, [0, 2])


def _validate_discount_group(branch_code: str, account_number: str) -> bool:
    full_number = account_number.zfill(9)
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    return _validate_mod11(full_number, weights, [0, 2, 4])


def _validate_mizrahi(branch_code: str, account_number: str) -> bool:
    adj_branch = int(branch_code)
    if 401 <= adj_branch <= 799:
        adj_branch -= 400
    full_number = str(adj_branch).zfill(3) + account_number.zfill(6)
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    return _validate_mod11(full_number, weights, [0, 2, 4])


def _validate_beinleumi_group(branch_code: str, account_number: str) -> bool:
    full_9_digits = branch_code.zfill(3) + account_number.zfill(6)
    weights_9 = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    if int(branch_code) in [347, 365, 384, 385]:
        return _validate_mod11(full_9_digits, weights_9, [0, 2])
    if int(branch_code) in [361, 362, 363]:
        return _validate_mod11(full_9_digits, weights_9, [0, 2, 4])
    if _validate_mod11(full_9_digits, weights_9, [0, 6]):
        return True
    account_6_digits = account_number.zfill(6)
    weights_6 = [6, 5, 4, 3, 2, 1]
    return _validate_mod11(account_6_digits, weights_6, [0, 6])


def _validate_postal_bank(branch_code: str, account_number: str) -> bool:
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    total = _calculate_weighted_sum_left_to_right(account_number, weights)
    return total % 10 == 0


def _validate_citibank(branch_code: str, account_number: str) -> bool:
    acc_norm = account_number.zfill(9)
    num_part = acc_norm[:-1]
    check_digit = int(acc_norm[-1])
    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    total = _calculate_weighted_sum_left_to_right(num_part, weights)
    remainder = total % 11
    return (11 - remainder) % 11 == check_digit


def _validate_hsbc(branch_code: str, account_number: str) -> bool:
    if not account_number.isdigit() or len(account_number) != 9:
        return False
    if int(branch_code) == 101:
        return account_number[6] in ["4", "9"]
    if int(branch_code) == 102:
        return account_number.endswith("001")
    return True


def _validate_one_zero(branch_code: str, account_number: str) -> bool:
    return _validate_mod97(branch_code, account_number)


def _validate_ash(branch_code: str, account_number: str) -> bool:
    if not account_number.isdigit() or len(account_number) != 9:
        return False
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    return _validate_mod11(account_number, weights, [0])


def _validate_global_remit(branch_code: str, account_number: str) -> bool:
    acc_norm = account_number.zfill(9)
    num_part = acc_norm[:-1]
    check_digit = int(acc_norm[-1])
    weights = [9, 8, 6, 4, 3, 7, 2, 5]
    total = _calculate_weighted_sum_left_to_right(num_part, weights)
    remainder = total % 11
    return (11 - remainder) % 11 == check_digit


def _validate_grow(branch_code: str, account_number: str) -> bool:
    if int(branch_code) >= 900:
        return True
    return _validate_mod97(branch_code, account_number, zero_pad_branch=False)


def _validate_ofek(branch_code: str, account_number: str) -> bool:
    return _validate_mod97(branch_code, account_number)


def _validate_nima(branch_code: str, account_number: str) -> bool:
    if not account_number.isdigit() or len(account_number) != 8:
        return False
    weights = [8, 7, 6, 5, 4, 3, 2, 1]
    return _validate_mod11(account_number, weights, [0, 2])


def _validate_rewire(branch_code: str, account_number: str) -> bool:
    if not account_number.isdigit() or len(account_number) != 9:
        return False
    weights = [1, 9, 2, 3, 4, 5, 6, 7, 8]
    return _validate_mod11(account_number, weights, [0])


def _validate_isracard(branch_code: str, account_number: str) -> bool:
    full_number = branch_code.zfill(3) + account_number.zfill(7)
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    return _validate_mod11(full_number, weights, [0], right_to_left=True)


def _validate_gmt(branch_code: str, account_number: str) -> bool:
    if int(branch_code) >= 900:
        return True
    return _validate_mod97(branch_code, account_number)


def _validate_019(branch_code: str, account_number: str) -> bool:
    acc_padded = account_number.zfill(9)
    return _validate_mod97(branch_code, acc_padded)


def _no_validation_rule(branch_code: str, account_number: str) -> bool:
    return True


VALIDATORS = {
    1: _validate_isracard,
    3: _validate_ash,
    4: _validate_yahav,
    9: _validate_postal_bank,
    10: _validate_leumi,
    11: _validate_discount_group,
    12: _validate_hapoalim,
    13: _no_validation_rule,
    14: _validate_beinleumi_group,
    15: _validate_ofek,
    17: _validate_discount_group,
    18: _validate_one_zero,
    20: _validate_mizrahi,
    21: _validate_nima,
    22: _validate_citibank,
    23: _validate_hsbc,
    31: _validate_beinleumi_group,
    35: _validate_grow,
    39: _no_validation_rule,
    46: _validate_beinleumi_group,
    47: _validate_global_remit,
    52: _validate_beinleumi_group,
    54: _no_validation_rule,
    58: _validate_rewire,
    69: _validate_gmt,
    79: _validate_019,
}


def validate_israeli_bank_account(
    bank_code: int, branch_code: int, account_number: str
) -> bool:
    if not all(
        isinstance(arg, T)
        for arg, T in zip([bank_code, branch_code, account_number], [int, int, str])
    ):
        raise InvalidBankAccountException(
            "Invalid input types. Expected (int, int, str)."
        )
    clean_account_number = account_number.strip()
    if not clean_account_number.isdigit():
        raise InvalidBankAccountException("Account number must contain only digits.")
    validator_func = VALIDATORS.get(bank_code)
    if validator_func is None:
        raise InvalidBankAccountException(
            f"Bank with code '{bank_code}' is not supported or does not exist."
        )
    return validator_func(str(branch_code), clean_account_number)
