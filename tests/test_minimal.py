import datetime

def test_minimal_datetime():
    now = datetime.datetime.now()
    assert isinstance(now, datetime.datetime)