'''
Utility functions to manipulate date and time.
'''
import pytz

from datetime import datetime
from dateutil import relativedelta

from typing import Dict

from fbpyutils import logging

def delta(x: datetime, y: datetime, delta: str = 'months') -> int:
    '''
    Gets the time delta between two dates.
     Parameters:
        x (datetime): The last date.
        y (datetime): The first date. Must be greater than or equal to the last date.
        delta (str): The unit of time to return. Should be either 'months' for the number of
        months between both dates or 'years' for the number of years between both dates.
        Defaults to 'months'.
     Returns:
        int: The number of months or years between both dates.
    '''
    logging.debug(f"Starting delta with x: {x}, y: {y}, delta: {delta}")
    d = relativedelta.relativedelta(x, y)
    if delta == 'months':
        logging.debug(f"Calculated delta in months: {d.years * 12 + d.months}")
        return d.years * 12 + d.months
    elif delta == 'years':
        logging.debug(f"Calculated delta in years: {d.years}")
        return d.years
    else:
        logging.error(f"Invalid option for delta: {delta}. Use 'months' or 'years'.")
        raise Exception('Invalid option. Use months or years')


def apply_timezone(x: datetime, tz: str) -> datetime:
    '''
    Apply the specified timezone to a datetime object.
     Parameters:
        x (datetime): The datetime to have the timezone applied.
        tz (str): The name of the timezone.
     Returns:
        datetime: The datetime object with the timezone information.
    '''
    logging.debug(f"Starting apply_timezone with datetime: {x}, timezone: {tz}")
    try:
        timezone = pytz.timezone(tz)
    except pytz.UnknownTimeZoneError as e:
        logging.error(f"Unknown timezone '{tz}': {e}")
        raise e

    date_time_obj = x

    result = datetime(
        date_time_obj.year, date_time_obj.month, date_time_obj.day,
        hour=date_time_obj.hour, minute=date_time_obj.minute, second=date_time_obj.second,
        microsecond=date_time_obj.microsecond, tzinfo=timezone)
    logging.debug(f"Finished apply_timezone successfully. Result: {result}")
    return result


def elapsed_time(x: datetime, y: datetime) -> tuple:
    '''
    Calculates and returns the elapsed time as a tuple (days, hours, minutes, seconds).
     Parameters:
        x (datetime): The last date.
        y (datetime): The first date. Must be greater than or equal to the last date.
     Returns:
        tuple: The elapsed time formatted as a tuple (days, hours, minutes, seconds).
    '''
    logging.debug(f"Starting elapsed_time with x: {x}, y: {y}")
    if x < y:
        logging.error(f"Invalid input for elapsed_time: x ({x}) must be greater than or equal to y ({y}).")
        raise ValueError("x parameter must be greater than or equal to y parameter")

    delta = x - y

    days = delta.days
    hours = delta.seconds//3600
    minutes = (delta.seconds//60)%60
    seconds = delta.seconds%60

    logging.debug(f"Finished elapsed_time successfully. Result: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")
    return days, hours, minutes, seconds
