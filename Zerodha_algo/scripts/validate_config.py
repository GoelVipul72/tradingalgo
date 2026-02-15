"""Simple config validation checks for Zerodha_algo project."""
from pathlib import Path
import sys
from pathlib import Path
# ensure project root is on sys.path so 'config' package can be imported
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import credentials, settings


def check_credentials():
    issues = []
    if not credentials.has_valid_credentials():
        issues.append("API_KEY and/or ACCESS_TOKEN are missing or placeholders in config/credentials.py or .env")
    if not credentials.API_SECRET:
        issues.append("API_SECRET is empty - required to generate new access tokens")
    if credentials.MODE not in ("PAPER", "LIVE"):
        issues.append(f"MODE '{credentials.MODE}' is unexpected. Use PAPER or LIVE")
    return issues


def check_settings():
    issues = []
    s = settings
    if not isinstance(s.SYMBOLS, (list, tuple)) or not s.SYMBOLS:
        issues.append("SYMBOLS must be a non-empty list")
    if not (0 < s.RISK_PER_TRADE < 1):
        issues.append("RISK_PER_TRADE should be between 0 and 1")
    if not (0 < s.DAILY_MAX_LOSS < 1):
        issues.append("DAILY_MAX_LOSS should be between 0 and 1")
    if s.FAST_EMA >= s.SLOW_EMA:
        issues.append("FAST_EMA should be smaller than SLOW_EMA")
    if not (0 < s.TRAILING_SL_PCT if hasattr(s, 'TRAILING_SL_PCT') else True):
        pass
    # TRAIL_SL_PCT is interpreted as percent in code (divided by 100). Ensure reasonable range
    if hasattr(s, 'TRAIL_SL_PCT'):
        val = s.TRAIL_SL_PCT
        if not (0 < val < 100):
            issues.append("TRAIL_SL_PCT looks out of expected range (0-100 percent)")
        elif val < 0.1:
            issues.append("TRAIL_SL_PCT is very small (<0.1%). Confirm intended value")
    if not isinstance(s.TIMEFRAME, str) or s.TIMEFRAME == "":
        issues.append("TIMEFRAME should be a non-empty string, e.g., '5minute'")
    if not (isinstance(s.START_TIME, tuple) and isinstance(s.END_TIME, tuple)):
        issues.append("START_TIME and END_TIME should be tuples like (9,20)")
    else:
        if s.START_TIME >= s.END_TIME:
            issues.append("START_TIME should be earlier than END_TIME")
    if s.CAPITAL <= 0:
        issues.append("CAPITAL must be positive")
    if s.MAX_TRADES_PER_DAY <= 0:
        issues.append("MAX_TRADES_PER_DAY should be a positive integer")
    return issues


def check_files():
    issues = []
    root = Path(__file__).resolve().parents[1]
    gitignore = (root / '.gitignore').read_text() if (root / '.gitignore').exists() else ''
    if '.env' not in gitignore:
        issues.append('.env is not present in .gitignore')
    if not (root / '.env').exists():
        issues.append('.env file not present; create from .env.example')
    return issues


def main():
    all_issues = []
    all_issues.extend(check_credentials())
    all_issues.extend(check_settings())
    all_issues.extend(check_files())

    if not all_issues:
        print('Config validation: OK')
        return 0

    print('Config validation: FOUND ISSUES:')
    for it in all_issues:
        print(' -', it)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
