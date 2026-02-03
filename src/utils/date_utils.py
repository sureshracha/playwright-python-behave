
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Union, Optional


def add_no_of_days(dt: datetime, days: int) -> datetime:
    """Add N days to a datetime (like JS setDate(getDate()+days))."""
    return dt + timedelta(days=days)


def subtract_no_of_days(dt: datetime, days: int) -> datetime:
    """Subtract N days from a datetime."""
    return dt - timedelta(days=days)


def get_dates(start_date: datetime, stop_date: datetime) -> List[datetime]:
    """
    Return list of datetimes from start_date to stop_date inclusive.
    Mirrors TS while(currentDate <= stopDate) with +1 day steps.
    """
    date_array: List[datetime] = []
    current = start_date

    while current <= stop_date:
        # Create a "copy" like new Date(currentDate)
        date_array.append(datetime.fromtimestamp(current.timestamp()))
        current = add_no_of_days(current, 1)

    return date_array


def get_mmddyyyy_format(dt: datetime) -> str:
    """Format as MM/DD/YYYY."""
    return dt.strftime("%m/%d/%Y")


def get_mmddyyyy_format_with_hyphen(dt: datetime) -> str:
    """Format as MM-DD-YYYY."""
    return dt.strftime("%m-%d-%Y")


def get_system_datetime_mmddyyyy_hhmm_format(now: Optional[datetime] = None) -> str:
    """
    Format current system time as: MM/DD/YYYY HH:MM AM/PM
    Matches your TS logic (12-hour clock with AM/PM).
    """
    now = now or datetime.now()
    return now.strftime("%m/%d/%Y %I:%M %p")


def get_system_datetime_yyyymmdd_hhmm_format(
    date_value: Union[str, int, float, datetime, None] = None
) -> str:
    """
    Format as: YYYY-MM-DDTHH:MM (24-hour clock)
    TS version accepts string|number|Date and uses new Date(date) or new Date().
    
    Python parsing notes:
      - datetime -> used directly
      - None or "" -> now
      - int/float -> treated as Unix seconds
      - str -> ISO-ish strings work best (e.g., "2026-01-30T10:15:00")
    """
    if date_value is None or date_value == "":
        dt = datetime.now()
    elif isinstance(date_value, datetime):
        dt = date_value
    elif isinstance(date_value, (int, float)):
        dt = datetime.fromtimestamp(date_value)
    elif isinstance(date_value, str):
        # Try ISO parse first
        try:
            dt = datetime.fromisoformat(date_value)
        except ValueError:
            # Fallback: attempt common formats (extend if you need more)
            for fmt in ("%m/%d/%Y %H:%M", "%m/%d/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    dt = None
            if dt is None:
                raise ValueError(f"Unrecognized date string format: {date_value!r}")
    else:
        raise TypeError(f"Unsupported type for date_value: {type(date_value)}")

    return dt.strftime("%Y-%m-%dT%H:%M")


def calculate_age(dob: str, today: Optional[datetime] = None) -> int:
    """
    Calculate age in years from date-of-birth string.
    Mirrors TS logic: subtract years and adjust if birthday not yet occurred.
    
    Accepts ISO-like dob strings best: "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS".
    """
    # Prefer ISO; fallback to common formats
    try:
        birth = datetime.fromisoformat(dob)
    except ValueError:
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                birth = datetime.strptime(dob, fmt)
                break
            except ValueError:
                birth = None
        if birth is None:
            raise ValueError(f"Unrecognized DOB format: {dob!r}")

    today = today or datetime.now()

    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age
