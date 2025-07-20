'''
Utility functions to manipulate date and time.
'''
import pytz

from datetime import datetime
from dateutil import relativedelta

from typing import Dict

from fbpyutils.logging import Logger

def delta(x: datetime, y: datetime, delta: str = 'months') -> int:
    """
    Calculates the time delta between two dates in months or years.

    Args:
        x (datetime): The later datetime object.
        y (datetime): The earlier datetime object.
        delta (str): The unit for the delta ('months' or 'years').
            Defaults to 'months'.

    Returns:
        int: The total number of months or years between the two dates.

    Example:
        >>> from datetime import datetime
        >>> date1 = datetime(2023, 1, 1)
        >>> date2 = datetime(2024, 3, 1)
        >>> delta(date2, date1, 'months')
        14
        >>> delta(date2, date1, 'years')
        1
    """
    Logger.debug(f"Starting delta with x: {x}, y: {y}, delta: {delta}")
    d = relativedelta.relativedelta(x, y)
    if delta == 'months':
        Logger.debug(f"Calculated delta in months: {d.years * 12 + d.months}")
        return d.years * 12 + d.months
    elif delta == 'years':
        Logger.debug(f"Calculated delta in years: {d.years}")
        return d.years
    else:
        Logger.error(f"Invalid option for delta: {delta}. Use 'months' or 'years'.")
        raise Exception('Invalid option. Use months or years')


def apply_timezone(x: datetime, tz: str) -> datetime:
    """
    Applies a specified timezone to a naive datetime object.

    Args:
        x (datetime): The naive datetime object.
        tz (str): The string name of the timezone (e.g., 'America/Sao_Paulo').

    Returns:
        datetime: A new datetime object with the specified timezone.

    Raises:
        pytz.UnknownTimeZoneError: If the timezone name is not found.

    Example:
        >>> from datetime import datetime
        >>> naive_dt = datetime(2024, 7, 19, 12, 0, 0)
        >>> apply_timezone(naive_dt, 'America/New_York')
        datetime.datetime(2024, 7, 19, 12, 0, tzinfo=<DstTzInfo 'America/New_York' EDT-1 day, 20:00:00 DST>)
    """
    Logger.debug(f"Starting apply_timezone with datetime: {x}, timezone: {tz}")
    try:
        timezone = pytz.timezone(tz)
    except pytz.UnknownTimeZoneError as e:
        Logger.error(f"Unknown timezone '{tz}': {e}")
        raise e

    date_time_obj = x

    result = datetime(
        date_time_obj.year, date_time_obj.month, date_time_obj.day,
        hour=date_time_obj.hour, minute=date_time_obj.minute, second=date_time_obj.second,
        microsecond=date_time_obj.microsecond, tzinfo=timezone)
    Logger.debug(f"Finished apply_timezone successfully. Result: {result}")
    return result


def elapsed_time(x: datetime, y: datetime) -> tuple:
    """
    Calculates the elapsed time between two datetime objects.

    Args:
        x (datetime): The later datetime object.
        y (datetime): The earlier datetime object.

    Returns:
        tuple: A tuple containing (days, hours, minutes, seconds).

    Raises:
        ValueError: If 'x' is earlier than 'y'.

    Example:
        >>> from datetime import datetime, timedelta
        >>> end_time = datetime(2024, 1, 2, 14, 30, 50)
        >>> start_time = datetime(2024, 1, 1, 12, 0, 0)
        >>> elapsed_time(end_time, start_time)
        (1, 2, 30, 50)
    """
    Logger.debug(f"Starting elapsed_time with x: {x}, y: {y}")
    if x < y:
        Logger.error(f"Invalid input for elapsed_time: x ({x}) must be greater than or equal to y ({y}).")
        raise ValueError("x parameter must be greater than or equal to y parameter")

    delta = x - y

    days = delta.days
    hours = delta.seconds//3600
    minutes = (delta.seconds//60)%60
    seconds = delta.seconds%60

    Logger.debug(f"Finished elapsed_time successfully. Result: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")
    return days, hours, minutes, seconds
