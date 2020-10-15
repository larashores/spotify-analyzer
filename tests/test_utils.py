import datetime
from typing import List, Tuple
from unittest import mock

import pytest

import utils
from track import Track


@pytest.mark.parametrize(
    "track, month",
    (
        (
            mock.Mock(start=datetime.datetime(2020, 12, 31, 23, 58), end=datetime.datetime(2021, 1, 1, 0, 1)),
            datetime.date(2020, 12, 1),
        ),
        (
            mock.Mock(start=datetime.datetime(2020, 12, 31, 23, 59), end=datetime.datetime(2021, 1, 1, 0, 1, 1)),
            datetime.date(2021, 1, 1),
        ),
        (
            mock.Mock(start=datetime.datetime(2020, 7, 7), end=datetime.datetime(2020, 7, 7, 1, 3)),
            datetime.date(2020, 7, 1),
        ),
    ),
)
def test_in_month(track: Track, month: datetime.date):
    assert utils.in_month(track) == month


@pytest.mark.parametrize(
    "track, day",
    (
        (
            mock.Mock(start=datetime.datetime(2020, 12, 31, 23, 58), end=datetime.datetime(2021, 1, 1, 0, 1)),
            datetime.date(2020, 12, 31),
        ),
        (
            mock.Mock(start=datetime.datetime(2020, 12, 31, 23, 59), end=datetime.datetime(2021, 1, 1, 0, 1, 1)),
            datetime.date(2021, 1, 1),
        ),
        (
            mock.Mock(start=datetime.datetime(2020, 7, 6, 23, 59), end=datetime.datetime(2020, 7, 7, 1, 3)),
            datetime.date(2020, 7, 7),
        ),
    ),
)
def test_in_day(track: Track, day: datetime.date):
    assert utils.in_day(track) == day


@pytest.mark.parametrize(
    "duration, hours_minutes_seconds",
    (
        (datetime.timedelta(hours=10), (10, 0, 0)),
        (datetime.timedelta(minutes=10), (0, 10, 0)),
        (datetime.timedelta(seconds=10), (0, 0, 10)),
        (datetime.timedelta(hours=10, minutes=9, seconds=8), (10, 9, 8)),
        (datetime.timedelta(days=2, hours=2, seconds=1), (50, 0, 1)),
    ),
)
def test_hours_minutes_seconds(duration: datetime.timedelta, hours_minutes_seconds: Tuple[int, int, int]):
    assert utils.hours_minutes_seconds(duration) == hours_minutes_seconds


@pytest.mark.parametrize(
    "length, values, averages",
    (
        (5, (1, 1, 1, 1, 1), [1.0, 1.0, 1.0, 1.0, 1.0]),
        (5, (1, 1, 2, 1, 1), [1.4, 1.2, 1.2, 1.2, 1.4]),
        (5, (1, 1, 1, 1, 5, 3, 5, 1, 1, 1), [1.0, 1.0, 1.8, 2.2, 3.0, 3.0, 3.0, 2.2, 2.6, 1.0]),
    ),
)
def test_moving_average(length: int, values: Tuple[float], averages: List[float]):
    assert utils.moving_average(values, length) == averages
