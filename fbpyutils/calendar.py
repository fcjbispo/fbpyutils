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
    Build a calendar to be used as a time dimension.
     Parameters:
        x (date): The initial date for the calendar.
        y (date): The final date for the calendar. Must be greater than the initial date.
     Returns:
        List: A calendar to be used as a time dimension with the following attributes:
            - date (date): The date.
            - date_time (datetime): The date and time.
            - year (int): The year.
            - half (int): The half of the year.
            - quarter (int): The quarter of the year.
            - month (int): The month.
            - day (int): The day.
            - week_day (int): The day of the week (Monday is 0 and Sunday is 6).
            - week_of_year (int): The week of the year.
            - date_iso (str): The date in ISO format.
            - date_str (str): The date in string format.
            - week_day_name (str): The name of the day of the week.
            - week_day_name_short (str): The short name of the day of the week.
            - week_month_name (str): The name of the month.
            - week_month_name_short (str): The short name of the month.
            - year_str (str): The year in string format.
            - year_half_str (str): The year and half of the year in string format.
            - year_quarter_str (str): The year and quarter of the year in string format.
            - year_month_str (str): The year and month in string format.
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
    Adds markers to past months from the reference date.
     Parameters:
        x (List): The calendar dict used to add markers.
        reference_date (date): The date used to calculate the markers. Defaults to the current date.
     Returns:
        List: The calendar with added markers. The markers indicate the number of months past from the reference date:
            - today (bool): True if the calendar date and the current date are the same.
            - current_year (bool): True if the calendar date's year is the current year.
            - last_day_of_month (bool): True if the calendar date is the last date of its month.
            - last_day_of_quarter (bool): True if the calendar date is the last date of its quarter.
            - last_day_of_half (bool): True if the calendar date is the last date of its half.
            - last_day_of_year (bool): True if the calendar date is the last date of its year.
            - last_24_months (bool): True if the calendar date is within the last 24 months from the current date.
            - last_12_months (bool): True if the calendar date is within the last 12 months from the current date.
            - last_6_months (bool): True if the calendar date is within the last 6 months from the current date.
            - last_3_months (bool): True if the calendar date is within the last 3 months from the current date.
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
    print(f"markers = {markers}")
    for c in cal:
        last_day_month = c['date'] == markers[c['year_month_str']]
        print(f"c['date'] = {c['date']}, markers[c['year_month_str']] = {markers[c['year_month_str']]}, last_day_month = {last_day_month}")
        c.update({
            'today': today == c['date'],
            'current_year': today.year == c['date'].year,
            'last_day_of_month': last_day_month,
            'last_day_of_quarter': c['date'] == markers[
                c['year_quarter_str']],
            'last_day_of_half': c['date'] == markers[c['year_half_str']],
            'last_day_of_year': c['date'] == markers[c['year_str']],
            'last_24_months': dutl.delta(today, c['date'], 'months') <= 24,
            'last_12_months': dutl.delta(today, c['date'], 'months') <= 12,
            'last_6_months': dutl.delta(today, c['date'], 'months') <= 6,
            'last_3_months': dutl.delta(today, c['date'], 'months') <= 3,
        })

    return cal

def calendarize(
    x: DataFrame,
    date_column: str,
    with_markers: bool = False,
    reference_date: date = datetime.now().date()
) -> DataFrame:
    '''
    Adds calendar columns to a dataframe.
     Parameters:
        x (DataFrame): The dataframe used to add calendar data.
        date_column (str): The datetime column used to build calendar data. Should be different from 'calendar_date'.
        with_markers (bool): Indicates whether to add calendar markers to the dataframe. Default is False.
        reference_date (date): The date used to calculate the markers. Defaults to the current date.
     Returns:
        DataFrame: A new dataframe with calendar columns and optional markers added to the passed dataframe.
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
