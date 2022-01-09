'''
Functions to manipulate calendars.
'''

from datetime import date, datetime
from pandas import DataFrame
import pandas as pd
import numpy as np

from typing import Dict, List

from fbpyutils import datetime as dutl


def get_calendar(x: date, y: date) -> List:
    '''
    Build a calendar for use as time dimension

        x
            Intial date for the calendar

        y
            Final date for the calendar. Must be greater than initial date

        Return a calendar for use as time dimension with the following
        attributes:
            date, date_time, year, half, quarter, month, day,
            week_day, week_of_year, date_iso, date_str, week_day_name,
            week_day_name_short, week_month_name, week_month_name_short,
            year_str, year_half_str, year_quarter_str, year_month_str
    '''
    start_date, end_date = x, y
    if end_date <= start_date:
        raise ValueError("Invalid end date. Must be greater than start date.")

    cal = None
    try:
        dates = pd.date_range(start_date, end_date)
        cal = [
            {
                "date": d.date(),
                "date_time": d,
                "year": d.year,
                "half": (d.quarter + 1) // 2,
                "quarter": d.quarter,
                "month": d.month,
                "day": d.day,
                "week_day": d.weekday(),
                "week_of_year": int(d.strftime('%W')),
                "date_iso": d.isoformat(),
                "date_str": d.strftime('%Y-%m-%d'),
                "week_day_name": d.strftime('%A'),
                "week_day_name_short": d.strftime('%a'),
                "week_month_name": d.strftime('%B'),
                "week_month_name_short": d.strftime('%b'),
                "year_str": d.strftime('%Y'),
                "year_half_str": d.strftime('%Y-H') + str((d.quarter + 1) // 2),
                "year_quarter_str": d.strftime('%Y-Q') + str(d.quarter),
                "year_month_str": d.strftime('%Y-%m'),
            } for d in dates
        ]
    except ValueError as e:
        raise e

    return cal


def add_markers(
    x: List, reference_date: date = datetime.now().date()
) -> List:
    '''
    Adds markers to past months from reference date

        x
            The calendar dict used to add markers

        reference_date
            The date used to calculate the markers. Default to current date

        Add markers to the passed calendar. The markets are flags
        the the number of months past ago from reference date:
            today: True if calendar date and current date are the same
            current_year: True if calendar date's year is the current year
            last_day_of_month: True if calendar date is the last date of
                the date's month
            last_day_of_quarter: True if calendar date is the last date of
                the date's quarter
            last_day_of_half: True if calendar date is the last date of
                the date's half
            last_day_of_year: True if calendar date is the last date of
                the date's year
            last_24_months: True if calendar date is in the last 24 months
                from current date
            last_12_months: True if calendar date is in the last 12 months
                from current date
            last_6_months: True if calendar date is in the last 6 months
                from current date
            last_3_months: True if calendar date is in the last 3 months
                from current date
    '''
    cal = x

    markers = {}
    markers.update({
        m: max([
            c['date'] for c in cal if c['year_str'] == m]
            ) for m in set(c['year_str'] for c in cal)})
    markers.update({
        m: max([
            c['date'] for c in cal if c['year_half_str'] == m]
            ) for m in set(c['year_half_str'] for c in cal)})
    markers.update({
        m: max([
            c['date'] for c in cal if c['year_quarter_str'] == m]
            ) for m in set(c['year_quarter_str'] for c in cal)})
    markers.update({
        m: max([
            c['date'] for c in cal if c['year_month_str'] == m]
            ) for m in set(c['year_month_str'] for c in cal)})

    today = datetime.now().date()
    for c in cal:
        c.update({
            'today': today == c['date'],
            'current_year': today.year == c['date'].year,
            'last_day_of_month': c['date'] == markers[c['year_month_str']],
            'last_day_of_quarter': c['date'] == markers[
                c['year_quarter_str']],
            'last_day_of_half': c['date'] == markers[c['year_half_str']],
            'last_day_of_year': c['date'] == markers[c['year_str']],
            'last_24_months': dutl.delta(today, c['date'], 'months') <= 24,
            'last_12_months': dutl.delta(today, c['date'], 'months') <= 12,
            'last_6_months': dutl.delta(today, c['date'], 'months') <= 6,
            'last_3_months': dutl.delta(today, c['date'], 'months') <= 3,
        })


def calendarize(
    x: DataFrame,
    date_column: str,
    with_markers: bool = False,
    reference_date: date = datetime.now().date()
) -> DataFrame:
    '''
    Adds calendar columns to a dataframe

        x
            The dataframe used to add calendar data

        date_column
            The datetime column used to build calendar data.
            Shoud be different from 'calendar_date'

        with_markers
            Add or not calendar markers to the dataframe. Default False

        reference_date
            The date used to calculate the markers. Default to current date

        Return a new dataframe with calendar columns and optional markers added 
        to the passed dataframe.
    '''
    if not type(x) == type(pd.DataFrame([])):
        raise TypeError(f'Invalid object type. Expected Pandas DataFrame.')

    if not type(reference_date) == type(datetime.now().date()):
        raise TypeError(f'Invalid object type. Expected Date/Datetime object.')

    df = x.copy()

    if (
        date_column not in df.columns or
        not np.issubdtype(df[date_column], np.datetime64)
    ):
        raise NameError(f'DateTime column not found or invalid: {date_column}.')

    mind, maxd = min(df[date_column]), max(df[date_column])

    calendar = get_calendar(mind, maxd)
    if with_markers:
        add_markers(calendar, reference_date)

    calendar = pd.DataFrame.from_dict(calendar)

    columns = ['_'.join(['calendar', c]) for c in calendar.columns]
    calendar.columns = columns
    df[date_column] = df[date_column].dt.date

    return df.merge(
        calendar,
        left_on=date_column, right_on='calendar_date'
    )
