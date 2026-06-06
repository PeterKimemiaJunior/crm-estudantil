import re
import html
from typing import Iterable, Optional


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# Mozambique mobile prefixes (examples provided): 82,83,84,85,86,87
MZ_MOBILE_PREFIXES = ('82', '83', '84', '85', '86', '87')
MZ_E164_RE = re.compile(r'^\+258(?:' + '|'.join(p for p in MZ_MOBILE_PREFIXES) + r')\d{7}$')
MZ_NATIONAL_RE = re.compile(r'^0(?:' + '|'.join(p for p in MZ_MOBILE_PREFIXES) + r')\d{7}$')


def sanitize_text(value: Optional[object], max_len: int = 255) -> str:
    if value is None:
        return ''
    s = str(value).strip()
    # remove non-printable/control characters
    s = ''.join(ch for ch in s if ch.isprintable())
    # escape HTML characters to avoid injection in stored text
    s = html.escape(s)
    return s[:max_len]


def validate_email(value: Optional[str], max_len: int = 120) -> bool:
    if not value:
        return False
    s = str(value).strip()
    if len(s) > max_len:
        return False
    return bool(EMAIL_RE.match(s))


def sanitize_phone(value: Optional[object], max_len: int = 32) -> str:
    """Return a normalized Mozambican phone in E.164 (+258...) when possible.

    If the input is empty/None, returns empty string. If the phone cannot
    be recognised as a Mozambican mobile number, returns empty string.
    """
    if value is None:
        return ''
    s = str(value).strip()
    # remove spaces, parentheses and dashes for checking
    cleaned = ''.join(ch for ch in s if ch.isdigit() or ch == '+')
    # normalize local form starting with 0 (e.g., 0821234567) -> +258821234567
    if MZ_NATIONAL_RE.match(cleaned):
        return '+258' + cleaned[1:]
    # Already E.164 with +
    if MZ_E164_RE.match(cleaned):
        return cleaned
    # Allow forms with country code but without + (e.g., 258821234567)
    if cleaned.startswith('258') and MZ_E164_RE.match('+' + cleaned):
        return '+' + cleaned
    return ''


def validate_phone(value: Optional[object]) -> bool:
    """Return True if the value represents a valid Mozambican mobile number."""
    if not value:
        return False
    s = str(value).strip()
    cleaned = ''.join(ch for ch in s if ch.isdigit() or ch == '+')
    if MZ_E164_RE.match(cleaned):
        return True
    if MZ_NATIONAL_RE.match(cleaned):
        return True
    if cleaned.startswith('258') and MZ_E164_RE.match('+' + cleaned):
        return True
    return False


def sanitize_choice(value: Optional[object], allowed: Iterable[str], default: Optional[str] = None) -> Optional[str]:
    if value is None:
        return default
    s = str(value).strip()
    return s if s in allowed else default


def safe_int(value: Optional[object], default: int = 0, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    try:
        i = int(value)
    except Exception:
        return default
    if min_value is not None and i < min_value:
        return default
    if max_value is not None and i > max_value:
        return default
    return i


def safe_id(value: Optional[object]) -> Optional[int]:
    try:
        i = int(value)
    except Exception:
        return None
    return i if i > 0 else None
