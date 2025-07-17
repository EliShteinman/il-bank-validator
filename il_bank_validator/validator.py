# il_bank_validator/validator.py

from .exceptions import InvalidBankAccountException

# --- Helper Functions ---


def _calculate_weighted_sum(digits: str, weights: list[int]) -> int:
    """
    Calculates a weighted sum for a string of digits.
    The weights are applied from right to left on the digits.
    """
    total = 0
    reversed_digits = digits[::-1]
    for i, digit in enumerate(reversed_digits):
        if i < len(weights):
            total += int(digit) * weights[i]
    return total


def _validate_mod11(
    full_number: str, weights: list[int], valid_remainders: list[int]
) -> bool:
    """Generic MOD 11 validation logic."""
    if not full_number.isdigit():
        return False

    total = _calculate_weighted_sum(full_number, weights)
    return (total % 11) in valid_remainders


def _validate_mod97(
    branch_code: int, account_number: str, zero_pad_branch=True
) -> bool:
    """
    Generic MOD 97 validation logic (ISO 7064 style).
    Concatenates branch and account number before checking.
    """
    if not account_number.isdigit() or len(account_number) < 3:
        return False

    try:
        branch_str = str(branch_code).zfill(3) if zero_pad_branch else str(branch_code)
        num_part_str = branch_str + account_number[:-2]
        num_part_int = int(num_part_str)
        check_digits = int(account_number[-2:])

        # The check is performed as: 98 - (number % 97) should equal the check digits.
        # This is derived from examples in the MASAV document.
        calculated_check_digits = 98 - (num_part_int % 97)

        # In case the remainder is 1, 98-1=97. The check digit should be 97, not 0.
        # However, some systems might expect 0. The examples imply 97.
        # Let's trust the direct calculation: 98-27=71 for One Zero example.
        return calculated_check_digits == check_digits

    except (ValueError, TypeError):
        return False


# --- Bank-Specific Validation Functions ---


def _validate_leumi(branch_code: int, account_number: str) -> bool:
    """Validation for Bank Leumi (10). Based on MASAV rules, page 2."""
    acc_norm = account_number.zfill(8)
    if not acc_norm.isdigit() or len(acc_norm) != 8:
        return False

    # Sum is calculated on last digit of branch + first 6 digits of account
    acc_part_for_sum = str(branch_code % 10) + acc_norm[:-2]
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 10]  # These weights are described left-to-right
    base_sum = 0
    for i, digit in enumerate(acc_part_for_sum):
        base_sum += int(digit) * weights[i]

    check_digits = int(acc_norm[-2:])
    constants = [128, 180, 330, 340]
    if acc_norm[4:6] not in ["00", "20", "23"]:
        constants.append(110)

    for const in constants:
        total = base_sum + const
        remainder = total % 100
        calculated_check = 0 if remainder == 0 else 100 - remainder
        if calculated_check == check_digits:
            return True
    return False


def _validate_hapoalim(branch_code: int, account_number: str) -> bool:
    """Validation for Bank Hapoalim (12). Based on MASAV rules, page 3."""
    full_number = str(branch_code).zfill(3) + account_number.zfill(6)
    weights = [1, 6, 5, 4, 3, 2, 9, 8, 7]
    return _validate_mod11(full_number, weights, [0, 2, 4, 6])


def _validate_yahav(branch_code: int, account_number: str) -> bool:
    """Validation for Bank Yahav (04). Based on MASAV rules, page 3."""
    full_number = str(branch_code).zfill(3) + account_number.zfill(6)
    weights = [1, 6, 5, 4, 3, 2, 9, 8, 7]
    return _validate_mod11(full_number, weights, [0, 2])


def _validate_discount_group(branch_code: int, account_number: str) -> bool:
    """Validation for Discount Group (11, 17). Based on MASAV rules, page 4."""
    account_only_full = account_number.zfill(9)
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    total = _calculate_weighted_sum(account_only_full, weights)
    return (total % 11) in [0, 2, 4]


def _validate_mizrahi(branch_code: int, account_number: str) -> bool:
    """Validation for Mizrahi-Tefahot (20). Based on MASAV rules, page 4."""
    adj_branch = branch_code
    if 401 <= branch_code <= 799:
        adj_branch -= 400

    full_number = str(adj_branch).zfill(3) + account_number.zfill(6)
    weights = [1, 6, 5, 4, 3, 2, 9, 8, 7]
    return _validate_mod11(full_number, weights, [0, 2, 4])


def _validate_beinleumi_group(branch_code: int, account_number: str) -> bool:
    """Validation for FIBI Group (31, 52, 14, 46). Based on MASAV rules, pages 6-7."""
    full_9_digits = str(branch_code).zfill(3) + account_number.zfill(6)
    weights_9 = [1, 6, 5, 4, 3, 2, 9, 8, 7]

    # Special branch rules take precedence
    if branch_code in [347, 365, 384, 385]:
        return _validate_mod11(full_9_digits, weights_9, [0, 2])
    if branch_code in [361, 362, 363]:
        return _validate_mod11(full_9_digits, weights_9, [0, 2, 4])

    # Standard two-step validation
    if _validate_mod11(full_9_digits, weights_9, [0, 6]):
        return True

    account_6_digits = account_number.zfill(6)
    weights_6 = [1, 6, 5, 4, 3, 2]
    return _validate_mod11(account_6_digits, weights_6, [0, 6])


def _validate_postal_bank(branch_code: int, account_number: str) -> bool:
    """Validation for Postal Bank (09). Based on MASAV rules, page 8."""
    if not account_number.isdigit():
        return False
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    total = _calculate_weighted_sum(account_number, weights)
    return total % 10 == 0


def _validate_citibank(branch_code: int, account_number: str) -> bool:
    """Validation for Citibank (22). Based on MASAV rules, page 8."""
    acc_norm = account_number.zfill(9)
    if not acc_norm.isdigit() or len(acc_norm) != 9:
        return False

    num_part = acc_norm[:-1]
    check_digit = int(acc_norm[-1])
    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    total = _calculate_weighted_sum(num_part, weights)
    remainder = total % 11
    calculated_check = (11 - remainder) % 11
    return calculated_check == check_digit


def _validate_hsbc(branch_code: int, account_number: str) -> bool:
    """Validation for HSBC (23). Based on MASAV rules, page 9."""
    if not account_number.isdigit() or len(account_number) != 9:
        return False
    if branch_code == 101:
        return account_number[6] in ["4", "9"]
    if branch_code == 102:
        return account_number.endswith("001")
    return True


def _validate_one_zero(branch_code: int, account_number: str) -> bool:
    """Validation for One Zero Digital Bank (18). Based on MASAV rules, page 9."""
    return _validate_mod97(branch_code, account_number)


def _validate_ash(branch_code: int, account_number: str) -> bool:
    """Validation for Bank Ash (03). Based on MASAV rules, page 10."""
    if not account_number.isdigit() or len(account_number) != 9:
        return False
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    total = _calculate_weighted_sum(account_number, weights)
    return total % 11 == 0


def _validate_global_remit(branch_code: int, account_number: str) -> bool:
    """Validation for Global Remit (47). Based on MASAV rules, page 11."""
    acc_norm = account_number.zfill(9)
    if not acc_norm.isdigit() or len(acc_norm) != 9:
        return False

    num_part = acc_norm[:-1]
    check_digit = int(acc_norm[-1])
    weights = [5, 2, 7, 3, 4, 6, 8, 9]
    total = _calculate_weighted_sum(num_part, weights)
    remainder = total % 11
    return (11 - remainder) % 11 == check_digit


def _validate_grow(branch_code: int, account_number: str) -> bool:
    """Validation for GROW (35). Based on MASAV rules, page 11."""
    if branch_code >= 900:
        return True
    return _validate_mod97(branch_code, account_number, zero_pad_branch=False)


def _validate_ofek(branch_code: int, account_number: str) -> bool:
    """Validation for Ofek (15). Based on MASAV rules, page 12."""
    return _validate_mod97(branch_code, account_number)


def _validate_nima(branch_code: int, account_number: str) -> bool:
    """Validation for Nima Shefa Israel (21). Based on MASAV rules, page 12."""
    if not account_number.isdigit() or len(account_number) != 8:
        return False
    weights = [1, 2, 3, 4, 5, 6, 7, 8]
    total = _calculate_weighted_sum(account_number, weights)
    return (total % 11) in [0, 2]


def _validate_rewire(branch_code: int, account_number: str) -> bool:
    """Validation for Rewire (58). Based on MASAV rules, page 13."""
    if not account_number.isdigit() or len(account_number) != 9:
        return False
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2]
    total = _calculate_weighted_sum(account_number, weights)
    return total % 11 == 0


def _validate_isracard(branch_code: int, account_number: str) -> bool:
    """Validation for Isracard (01). Based on MASAV rules, page 13."""
    full_number = str(branch_code).zfill(3) + account_number.zfill(7)
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    total = _calculate_weighted_sum(full_number, weights)
    return (total % 11) == 0


def _validate_gmt(branch_code: int, account_number: str) -> bool:
    """Validation for GMT (69). Based on MASAV rules, page 14."""
    if branch_code >= 900:
        return True
    return _validate_mod97(branch_code, account_number)


def _validate_019(branch_code: int, account_number: str) -> bool:
    """Validation for 019 Sherutey Tashlum (79). Based on MASAV rules, page 15."""
    acc_padded = account_number.zfill(9)  # 7 digits + 2 check
    return _validate_mod97(branch_code, acc_padded)


def _no_validation_rule(branch_code: int, account_number: str) -> bool:
    """Placeholder for banks with no validation rule. Always returns True."""
    return True


# --- Main Dispatcher ---
VALIDATORS = {
    1: _validate_isracard,
    3: _validate_ash,
    4: _validate_yahav,
    9: _validate_postal_bank,
    10: _validate_leumi,
    11: _validate_discount_group,
    12: _validate_hapoalim,
    13: _no_validation_rule,  # Igud, merged
    14: _validate_beinleumi_group,  # Otsar HaHayal
    15: _validate_ofek,
    17: _validate_discount_group,  # Mercantile
    18: _validate_one_zero,
    20: _validate_mizrahi,
    21: _validate_nima,
    22: _validate_citibank,
    23: _validate_hsbc,
    31: _validate_beinleumi_group,  # FIBI
    35: _validate_grow,
    39: _no_validation_rule,  # Indian Bank
    46: _validate_beinleumi_group,  # Massad
    47: _validate_global_remit,
    52: _validate_beinleumi_group,  # PAGI
    54: _no_validation_rule,  # Jerusalem
    58: _validate_rewire,
    69: _validate_gmt,
    79: _validate_019,
}


def validate_israeli_bank_account(
    bank_code: int, branch_code: int, account_number: str
) -> bool:
    """
    Validates an Israeli bank account based on the bank code, branch code, and account number.
    Args:
        bank_code (int): The 2-digit code of the bank.
        branch_code (int): The 3-digit code of the branch.
        account_number (str): The account number, which may include check digits.
    Returns:
        bool: True if the account is valid according to MASAV rules, False otherwise.
    Raises:
        InvalidBankAccountException: If input types are invalid or the bank code is not supported.
    """
    if (
        not isinstance(bank_code, int)
        or not isinstance(branch_code, int)
        or not isinstance(account_number, str)
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

    return validator_func(branch_code, clean_account_number)
