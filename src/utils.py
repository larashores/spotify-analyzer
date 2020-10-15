import datetime
import logging
from typing import Any, Callable, Iterable, Sequence, Tuple, Union

from track import Track


def configure_logger(logger_name: str, file_name: str) -> None:
    formatter = logging.Formatter(datefmt="%Y-%m-%d %H:%M:%S", fmt="{asctime} {message}", style="{")
    handler = logging.FileHandler(file_name)
    handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.setLevel("INFO")
    logger.handlers = [handler]


def _start_of_month(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _start_of_day(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _pin(track: Track, pinner: Callable[[datetime.datetime], datetime.datetime]) -> datetime.datetime:
    pinned_end = pinner(track.end)
    return pinned_end if (track.end - pinned_end > pinned_end - track.start) else pinner(track.start)


def in_month(track: Track) -> datetime.date:
    return _pin(track, _start_of_month).date()


def in_day(track: Track) -> datetime.date:
    return _pin(track, _start_of_day).date()


def hours_minutes_seconds(duration: datetime.timedelta) -> Tuple[int, int, int]:
    seconds = duration.total_seconds()

    return int(seconds // 3600), int((seconds % 3600) // 60), int((seconds % 3600) % 60)


def pformat_table(
    rows: Iterable[Iterable[Any]],
    sep: Union[str, Sequence[str]] = ",",
    justify: Union[str, Sequence[str]] = "^",
    spacing: str = "",
) -> str:
    processed = [[f"{spacing}{item}{spacing}" for item in row] for row in rows]
    max_width = [0 for row in processed[0]]
    for row in processed:
        for ind, col in enumerate(row):
            max_width[ind] = max(max_width[ind], len(col))

    if isinstance(sep, str):
        format_spec = "".join(
            (
                ((sep if isinstance(sep, str) else sep[ind]) if ind != 0 else "")
                + f"{{:{justify if isinstance(justify, str) else justify[ind]}{width}}}"
            )
            for ind, width in enumerate(max_width)
        )

    return "\n".join(format_spec.format(*row) for row in processed)


def moving_average(values: Sequence[float], distance: int) -> Sequence[float]:
    averages = []

    for i in range(len(values)):
        total: Union[int, float] = 0
        for offset in range(-distance // 2 + 1, distance // 2 + 1):
            ind = i + offset
            if ind < 0 or ind >= len(values):
                ind = i - offset
            total += values[ind]
        averages.append(total / distance)

    return averages
