'''
Utility functions to manipulate date and time.
'''
import pytz

from datetime import datetime
from dateutil import relativedelta

from typing import Dict

def delta(x: datetime, y: datetime, delta: str = 'months') -> int:
    '''
    Gets time delta from two dates

        x
            Last date

        y
            First date. Must be greater or equal to the last date

       delta
            The unit of time to return. Should be either:
                'months' for number of months between
                    both dates
                'years' for number of years between both
                    dates

        Return the number of months or years between both dates
    '''
    d = relativedelta.relativedelta(x, y)
    if delta == 'months':
        return d.years * 12 + d.months
    elif delta == 'years':
        return d.years
    else:
        raise Exception('Invalid option. Use months or years')


def apply_timezone(x: datetime, tz: str) -> datetime:
    '''
    Apply the specified timezone to a datetime object

        x
            The datetime to have TZ applied
        y
            The TZ name

        Return the datetime object with TZ information
    '''
    timezone = pytz.timezone(tz)

    date_time_obj = x

    return datetime(
        date_time_obj.year, date_time_obj.month, date_time_obj.day, 
        hour=date_time_obj.hour, minute=date_time_obj.minute, second=date_time_obj.second,
        microsecond=date_time_obj.microsecond, tzinfo=timezone)


def elapsed_time(x: datetime, y: datetime) -> tuple:
    '''
    Calculates and return elapsed time as tuple (days, hours, minutes, seconds).

        x
            Last date

        y
            First date. Must be greater or equal to the last date

        Return the elapsed time formatted as tuple (days, hours, minutes, seconds)  
    '''
    delta = x - y

    days = delta.days
    hours = delta.seconds//3600
    minutes = (delta.seconds//60)%60
    seconds = delta.seconds%60

    return days, hours, minutes, seconds
