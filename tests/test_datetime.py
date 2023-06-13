import pytest
import datetime

from fbpyutils.datetime import delta


def test_delta_months():
    x = datetime.datetime(2023, 6, 1)
    y = datetime.datetime(2021, 6, 1)
    assert delta(x, y, 'months') == 24

def test_delta_years():
    x = datetime.datetime(2023, 6, 1)
    y = datetime.datetime(2021, 6, 1)
    assert delta(x, y, 'years') == 2

def test_delta_invalid_option():
    x = datetime.datetime(2023, 6, 1)
    y = datetime.datetime(2021, 6, 1)
    with pytest.raises(Exception):
        delta(x, y, 'invalid')