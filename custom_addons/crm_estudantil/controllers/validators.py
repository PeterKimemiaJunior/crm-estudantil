import re
import html
from typing import Iterable, Optional


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


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
    if value is None:
        return ''
    s = str(value)
    # keep digits and common punctuation
    s = ''.join(ch for ch in s if ch.isdigit() or ch in '+-() ')[:max_len]
    return s.strip()


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
