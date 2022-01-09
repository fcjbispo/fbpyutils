import pytest

from fbpyutils import calendar as cal, string as stu

from datetime import date
import pandas as pd

def setup_module(module):
    global date1, date2, date3
    global date_range1
    global dataframe1
    date1 = date(2020, 1, 1)
    date2 = date(2020, 12, 31)
    date3 = date(2021, 1, 1)
    date_range1 = len(pd.date_range(date1, date2))
    dataframe1 = pd.DataFrame(
        [
            (d, i, stu.random_string(5))
            for i, d in enumerate(pd.date_range(date1, date2))
        ], columns= [
            'date', 'index', 'name'
        ]
    )
    print(f"*** SETUP DONE ***")

def teardown_module(module):
    print(f"*** TEARDOWN DONE ***")

def test_get_calendar_with_valid_dates():
    c = cal.get_calendar(date1, date2)

    assert len(c) == date_range1

def test_get_calendar_with_invalid_date_order():
    with pytest.raises(ValueError):
        c = cal.get_calendar(date2, date1)

def test_get_calendar_with_invalid_date_types():
    with pytest.raises(ValueError):
        c = cal.get_calendar('date1', 'date2')

def test_add_markers_with_valid_data():
    c = cal.get_calendar(date1, date2)
    l1 = len(c[0].keys())

    cal.add_markers(c, date3)
    l2 = len(c[0].keys())

    assert l2 > l1

@pytest.mark.parametrize("with_markers", [(True), (False)])
def test_calendarize_with_markers(with_markers):
    c = cal.get_calendar(date1, date2)
    if with_markers:
        cal.add_markers(c, reference_date=date3)

    l1 = len(c[0].keys())

    dataframe2 = cal.calendarize(
        dataframe1, 'date', reference_date=date3, with_markers=with_markers)

    l2 = len(dataframe1.columns)
    l3 = len(dataframe2.columns)

    assert l3 == (l1 + l2)

@pytest.mark.parametrize("with_markers", [(True), (False)])
def test_calendarize_with_invalid_field_date(with_markers):
    with pytest.raises(NameError):
        dataframe2 = cal.calendarize(
            dataframe1, 'date_field', reference_date=date3, with_markers=with_markers)

@pytest.mark.parametrize("with_markers", [(True), (False)])
def test_calendarize_with_invalid_reference_date(with_markers):
    with pytest.raises(TypeError):
        dataframe2 = cal.calendarize(
            dataframe1, 'date', reference_date="date3", with_markers=with_markers)

@pytest.mark.parametrize("with_markers", [(True), (False)])
def test_calendarize_with_invalid_dataframe(with_markers):
    with pytest.raises(TypeError):
        dataframe2 = cal.calendarize(
            [], 'date', reference_date=date3, with_markers=with_markers)

