from freezegun import freeze_time
import pytest
from datetime import date, datetime
from fbpyutils.calendar import add_markers, calendarize, get_calendar
import pandas as pd


def test_get_calendar_valid_dates():
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 3)
    cal = get_calendar(start_date, end_date)
    assert len(cal) == 3
    assert cal[0]["date"] == start_date
    assert cal[-1]["date"] == end_date


def test_get_calendar_invalid_dates():
    start_date = date(2024, 1, 3)
    end_date = date(2024, 1, 1)
    with pytest.raises(ValueError):
        get_calendar(start_date, end_date)


def test_get_calendar_value_error():
    start_date = "invalid date"
    end_date = date(2024, 1, 3)
    with pytest.raises(TypeError):
        get_calendar(start_date, end_date)


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
    marked_cal = add_markers(cal)
    assert marked_cal[0]["last_day_of_month"] is False
    assert marked_cal[1]["last_day_of_month"] is True
    assert marked_cal[2]["last_day_of_month"] is False
    assert marked_cal[3]["last_day_of_month"] is True


@freeze_time("2024-02-01")  # Freeze time for consistent marker tests
def test_add_markers_markers():
    cal = [
        {
            "date": date(2024, 2, 1),
            "year_month_str": "2024-02",
            "year_quarter_str": "2024-1",
            "year_half_str": "2024-H1",
            "year_str": "2024",
        },
        {
            "date": date(2023, 2, 28),
            "year_month_str": "2023-02",
            "year_quarter_str": "2023-1",
            "year_half_str": "2023-H1",
            "year_str": "2023",
        },
    ]
    marked_cal = add_markers(cal)  # Using our corrected add_markers

    # For 2024-02-01
    assert marked_cal[0]["today"] is True
    assert marked_cal[0]["current_year"] is True
    assert (
        marked_cal[0]["last_day_of_month"] is False
    )  # because 2024-02-29 is the last day
    assert marked_cal[0]["last_day_of_quarter"] is False
    assert marked_cal[0]["last_day_of_half"] is False
    assert marked_cal[0]["last_day_of_year"] is False

    # For 2023-02-28 (using input marker for groups, and actual for year)
    assert marked_cal[1]["today"] is False
    assert marked_cal[1]["current_year"] is False
    assert marked_cal[1]["last_day_of_month"] is True  # only date in that month group
    assert (
        marked_cal[1]["last_day_of_quarter"] is True
    )  # only date in that quarter group
    assert (
        marked_cal[1]["last_day_of_half"] is True
    )  # only date in that half-year group
    assert (
        marked_cal[1]["last_day_of_year"] is False
    )  # actual last day of 2023 is 2023-12-31

    # The "last_X_months" markers depend on dutl.delta implementation.
    assert marked_cal[0]["last_24_months"] is True  # within 24 months of 2024-02-01
    assert marked_cal[1]["last_24_months"] is True
    assert marked_cal[0]["last_12_months"] is True
    assert marked_cal[1]["last_12_months"] is True
    assert marked_cal[0]["last_6_months"] is True
    assert marked_cal[1]["last_6_months"] is False
    assert marked_cal[0]["last_3_months"] is True
    assert marked_cal[1]["last_3_months"] is False


def test_add_markers_empty_calendar():
    cal = []
    marked_cal = add_markers(cal)
    assert marked_cal == []


def test_add_markers_invalid_calendar_entry():
    cal = [{"date": date(2024, 1, 1)}]  # Missing 'year_month_str'
    with pytest.raises(KeyError):
        add_markers(cal)


def test_calendarize_valid_dataframe():
    df = pd.DataFrame({"date_column": pd.to_datetime(["2024-01-01", "2024-01-02"])})
    calendar_df = calendarize(df, "date_column")
    assert "calendar_date" in calendar_df.columns
    assert "calendar_year" in calendar_df.columns


def test_calendarize_invalid_dataframe_type():
    with pytest.raises(TypeError):
        calendarize("invalid", "date_column")


def test_calendarize_invalid_date_column():
    df = pd.DataFrame({"date_column": pd.to_datetime(["2024-01-01", "2024-01-02"])})
    with pytest.raises(NameError):
        calendarize(df, "invalid_column")


def test_calendarize_invalid_datetime_column_type():
    df = pd.DataFrame({"date_column": ["2024-01-01", "2024-01-02"]})
    with pytest.raises(NameError):
        calendarize(df, "date_column")


def test_calendarize_with_markers():
    df = pd.DataFrame({"date_column": pd.to_datetime(["2024-01-01", "2024-01-02"])})
    calendar_df_with_markers = calendarize(
        df, "date_column", with_markers=True
    )
    assert "calendar_today" in calendar_df_with_markers.columns
    assert "calendar_current_year" in calendar_df_with_markers.columns
