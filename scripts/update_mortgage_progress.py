import os
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path


def read_amount(name: str) -> Decimal:
    value = os.environ.get(name, "").strip().replace(",", "")

    if not value:
        raise SystemExit(f"{name} is not configured")

    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise SystemExit(f"{name} must be a number")

    if amount < 0:
        raise SystemExit(f"{name} must not be negative")

    return amount


total = read_amount("MORTGAGE_TOTAL")
balance = read_amount("MORTGAGE_BALANCE")

if total <= 0:
    raise SystemExit("MORTGAGE_TOTAL must be greater than zero")

if balance > total:
    raise SystemExit("MORTGAGE_BALANCE must not exceed MORTGAGE_TOTAL")

paid = total - balance
progress = paid / total * Decimal("100")

bar_capacity = 30
filled = int(progress / Decimal("100") * bar_capacity)
filled = max(0, min(bar_capacity, filled))

progress_bar = "█" * filled + "▁" * (bar_capacity - filled)

updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")

replacement = (
    f"`{{ {progress_bar} }}` **{progress:.2f}%**  \n"
    f"  <sub>🤖 Updated by GitHub Actions · {updated_at}</sub>"
)

path = Path("README.md")
readme = path.read_text(encoding="utf-8")

pattern = r"(<!-- mortgage:start -->)" r".*?" r"(<!-- mortgage:end -->)"

updated, count = re.subn(
    pattern,
    rf"\1{replacement}\2",
    readme,
    flags=re.DOTALL,
)

if count != 1:
    raise SystemExit("Mortgage markers were not found exactly once in README.md")

path.write_text(updated, encoding="utf-8")
