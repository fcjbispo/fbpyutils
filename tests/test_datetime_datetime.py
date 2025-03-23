import pytest
from datetime import datetime
from fbpyutils import datetime as dutl


def test_delta_months():
    date1 = datetime(2024, 1, 1)
    date2 = datetime(2024, 3, 1)
    assert dutl.delta(date2, date1, "months") == 2


def test_delta_years():
    date1 = datetime(2020, 1, 1)
    date2 = datetime(2024, 1, 1)
    assert dutl.delta(date2, date1, "years") == 4


def test_delta_invalid_delta_type():
    date1 = datetime(2024, 1, 1)
    date2 = datetime(2024, 2, 1)
    with pytest.raises(Exception):
        dutl.delta(date2, date1, "invalid")


def test_apply_timezone():
    date1 = datetime(2024, 3, 23, 10, 0, 0)
    timezone = "US/Pacific"
    date_tz = dutl.apply_timezone(date1, timezone)
    assert date_tz.tzinfo is not None
    assert date_tz.tzinfo.zone == timezone


def test_elapsed_time_valid_dates():
    date1 = datetime(2024, 3, 1, 10, 0, 0)
    date2 = datetime(2024, 3, 2, 12, 30, 30)
    days, hours, minutes, seconds = dutl.elapsed_time(date2, date1)
    assert days == 1
    assert hours == 2
    assert minutes == 30
    assert seconds == 30


def test_elapsed_time_invalid_dates():
    date1 = datetime(2024, 3, 2, 12, 30, 30)
    date2 = datetime(2024, 3, 1, 10, 0, 0)
    with pytest.raises(ValueError):
        dutl.elapsed_time(date2, date1)
