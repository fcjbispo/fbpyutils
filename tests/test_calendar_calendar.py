import pytest
from datetime import date, datetime
from fbpyutils import calendar
import pandas as pd


def test_get_calendar_valid_dates():
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 3)
    cal = calendar.get_calendar(start_date, end_date)
    assert len(cal) == 3
    assert cal[0]["date"] == start_date
    assert cal[-1]["date"] == end_date


def test_get_calendar_invalid_dates():
    start_date = date(2024, 1, 3)
    end_date = date(2024, 1, 1)
    with pytest.raises(ValueError):
        calendar.get_calendar(start_date, end_date)


def test_add_markers_basic():
    cal = [
        {
            "date": date(2024, 1, 1),
            "year_month_str": "2024-01",
            "year_quarter_str": "2024-1",
            "year_half_str": "2024-H1",
            "year_str": "2024",
        },
        {
            "date": date(2024, 1, 31),
            "year_month_str": "2024-01",
            "year_quarter_str": "2024-1",
            "year_half_str": "2024-H1",
            "year_str": "2024",
        },
        {
            "date": date(2024, 2, 15),
            "year_month_str": "2024-02",
            "year_quarter_str": "2024-1",
            "year_half_str": "2024-H1",
            "year_str": "2024",
        },
        {
            "date": date(2024, 2, 29),
            "year_month_str": "2024-02",
            "year_quarter_str": "2024-1",
            "year_half_str": "2024-H1",
            "year_str": "2024",
        },
    ]
    reference_date = date(2024, 2, 15)
    marked_cal = calendar.add_markers(cal, reference_date)
    print(f"marked_cal[2]['last_day_of_month'] = {marked_cal[2]['last_day_of_month']}")
    assert marked_cal[0]["last_day_of_month"] == False
    assert marked_cal[1]["last_day_of_month"] == True
    assert marked_cal[2]["last_day_of_month"] == False  # 2024-02-15 is not last day
    assert marked_cal[3]["last_day_of_month"] == True  # 2024-02-29 is last day
