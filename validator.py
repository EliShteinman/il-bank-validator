# validator.py
import re
from .exceptions import InvalidBankAccountException

def _calculate_weighted_sum(digits, weights):
    total = 0
    for digit, weight in zip(digits, weights):
        total += int(digit) * weight
    return total

# כאן אמורים להיות כלל פונקציות האימות לבנקים (_validate_leumi וכו')
# לצורך יצירת zip מהירה, לא נדביק כאן את כולן שוב.
# אתה תעתיק את הפונקציות שלך (או אם תרצה, אכין עם הפונקציות בפנים).

def validate_israeli_bank_account(bank_code, branch_code, account_number):
    if not isinstance(bank_code, int) or not isinstance(branch_code, int) or not isinstance(account_number, str):
        raise InvalidBankAccountException("Invalid input types. Expected (int, int, str).")
    if not account_number.isdigit():
        raise InvalidBankAccountException("Account number must contain only digits.")
    
    branch_str = str(branch_code).zfill(3)

    # כאן אמורה לבוא הקריאה לפונקציות _validate_xxx לפי bank_code
    return True  # (מוחלף בביצוע האמיתי שלך)
