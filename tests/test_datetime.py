import pytest
import pytz
from datetime import datetime, timedelta

from fbpyutils.datetime import *


def test_delta_months():
    x = datetime(2023, 6, 1)
    y = datetime(2021, 6, 1)
    assert delta(x, y, 'months') == 24


def test_delta_years():
    x = datetime(2023, 6, 1)
    y = datetime(2021, 6, 1)
    assert delta(x, y, 'years') == 2


def test_delta_invalid_option():
    x = datetime(2023, 6, 1)
    y = datetime(2021, 6, 1)
    with pytest.raises(Exception):
        delta(x, y, 'invalid')

def test_apply_timezone():
    # test applying timezone
    x = datetime(2022, 1, 1, 12, 0, 0)
    tz = 'US/Eastern'
    result = apply_timezone(x, tz)
    assert result.strftime('%Y-%m-%d %H:%M:%S %Z%z') == '2022-01-01 12:00:00 LMT-0456'


def test_apply_timezone_invalid_tz():
    # test applying invalid timezone
    x = datetime(2022, 1, 1, 12, 0, 0)
    tz = 'Invalid Timezone'
    with pytest.raises(pytz.exceptions.UnknownTimeZoneError):
        result = apply_timezone(x, tz)


def test_elapsed_time():
    # test elapsed time calculation
    x = datetime(2022, 1, 1, 12, 0, 0)
    y = datetime(2021, 12, 31, 12, 0, 0)
    result = elapsed_time(x, y)
    assert result == (1, 0, 0, 0)


def test_elapsed_time_negative():
    # test elapsed time calculation with negative result
    x = datetime(2021, 12, 31, 12, 0, 0)
    y = datetime(2022, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError):
        result = elapsed_time(x, y)


def test_elapsed_time_same_date():
    # test elapsed time calculation with same date
    x = datetime(2022, 1, 1, 12, 0, 0)
    y = datetime(2022, 1, 1, 12, 0, 0)
    result = elapsed_time(x, y)
    assert result == (0, 0, 0, 0)


def test_elapsed_time_microseconds():
    # test elapsed time calculation with microseconds
    x = datetime(2022, 1, 1, 12, 0, 0, 500000)
    y = datetime(2021, 12, 31, 12, 0, 0, 500000)
    result = elapsed_time(x, y)
    assert result == (1, 0, 0, 0)