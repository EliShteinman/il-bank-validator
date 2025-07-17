# Changelog

כל השינויים והעדכונים ב־il-bank-validator.

---

## [0.2.0] - 2024-05-27
### Added
- Implemented complete validation logic for all banks listed in the MASAV document (rules effective May 2025).
- Added specific validation functions for ~20 bank groups including Leumi, Hapoalim, Mizrahi, Discount, One Zero, and new fintech banks like Ash, GROW, and Rewire.
- Created a modular dispatcher for easy extension and maintenance.
- Added a comprehensive test suite with examples directly from the MASAV document to ensure accuracy.

### Changed
- Refactored the main `validate_israeli_bank_account` function for robustness, clarity, and performance.
- Improved input validation to raise `InvalidBankAccountException` for malformed inputs or unsupported banks.

### Fixed
- Corrected validation logic based on detailed examples from the official MASAV PDF, including edge cases for specific branches and account types.

---

## [0.1.0] - 2025-04-27
- First official release on PyPI.
- Implements full Israeli banks validation based on MASAV rules (Dec 2024).
- Supports 22+ banks including Bank Leumi, Hapoalim, Mizrahi, Discount, Postal Bank, One Zero, and more.
