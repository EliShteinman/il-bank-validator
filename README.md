
# 🇮🇱 il-bank-validator / ולידטור לחשבונות בנק ישראליים

Validator for Israeli bank account numbers, based on MASAV (מס"ב) official rules - updated December 2024.
בודק תקינות חשבונות בנק לפי החוקים הרשמיים של מס"ב (עדכון דצמבר 2024).

[![PyPI version](https://badge.fury.io/py/il-bank-validator.svg)](https://pypi.org/project/il-bank-validator/)

---

## 📜 Introduction / מבוא

This package provides validation for Israeli bank accounts across multiple banks, using the official MASAV document as a standard reference.
הספריה מאפשרת אימות חשבונות בנק ישראליים במספר בנקים, לפי מסמך הנהלים של מס"ב.

---

## 📦 Installation / התקנה

```bash
pip install il-bank-validator
```

---

## 🚀 Quick Usage Example / דוגמת שימוש מהירה

```python
from il_bank_validator import validate_israeli_bank_account

# Example: Validate a Bank Leumi account
is_valid = validate_israeli_bank_account(10, 936, '07869660')
print(is_valid)  # True if valid
```

> פונקציה ראשית: `validate_israeli_bank_account(bank_code, branch_code, account_number)`
> מחזירה `True` אם החשבון תקין לפי הנהלים, אחרת `False`.

---

## 🏦 Supported Banks / בנקים נתמכים

- בנק לאומי
- בנק הפועלים
- דיסקונט
- מזרחי-טפחות
- בנק יהב
- דואר ישראל
- סיטי בנק
- HSBC
- בנק הדיגיטלי One Zero
- הבינלאומי הראשון
- בנק אוצר החייל
- מסד
- נאמה
- GROW
- Rewire
- Ofek
- Global Remit
- ועוד...

> Based on the official MASAV document:
> [MASAV Document Link](https://www.masav.co.il/media/2565/bdikat_hukiot_heshbon.pdf)

---

## 📋 Features / תכונות עיקריות

- Full compliance with updated MASAV rules (December 2024).
- Modular and extendable validator architecture.
- Supports both classic and newer banks (e.g., One Zero, Grow, Rewire).
- יכולת הרחבה לבנקים נוספים בעתיד.
- קוד ברור וקל לשילוב בפרויקטים אחרים.

---

## 🛠 Project Structure / מבנה הפרויקט

```text
il_bank_validator/
    __init__.py
    validator.py
    exceptions.py
tests/
    test_validator.py
README.md
CHANGELOG.md
LICENSE
pyproject.toml
setup.cfg
```

---

## ✍🏼 Contributing / תרומות קוד

We welcome community contributions!
נשמח לכל תרומה לקוד — פתיחת Issues, Pull Requests או שיפורים למסמכים.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a Pull Request.

---

## 📄 License / רישיון

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
פרויקט זה מופץ תחת רישיון MIT. מידע נוסף בקובץ הרישיון.

---

## 🌐 Links / קישורים חשובים

- [PyPI Project Page](https://pypi.org/project/il-bank-validator/)
- [GitHub Repository](https://github.com/EliShteinman/il-bank-validator)
- [MASAV Official Document (Dec 2024)](https://www.masav.co.il/media/2565/bdikat_hukiot_heshbon.pdf)

---

## 📫 Contact / יצירת קשר

For any inquiries, feel free to open an Issue or contact via GitHub.
לכל שאלה או בקשה — ניתן לפתוח Issue במאגר הגיט.

---
