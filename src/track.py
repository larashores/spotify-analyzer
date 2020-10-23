import dataclasses
import datetime
from typing import TypedDict

from backports import zoneinfo


def _fmt_time(timestamp: str) -> datetime.datetime:
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")


@dataclasses.dataclass(frozen=True)
class Track:
    artist: str
    track: str
    start: datetime.datetime
    end: datetime.datetime
    duration: datetime.timedelta

    class JSON(TypedDict):
        endTime: str
        artistName: str
        trackName: str
        msPlayed: int

    @staticmethod
    def from_json(data: JSON):
        end = _fmt_time(data["endTime"])
        start = end - datetime.timedelta(milliseconds=data["msPlayed"])
        return Track(
            artist=data["artistName"],
            track=data["trackName"],
            start=start,
            end=end,
            duration=datetime.timedelta(milliseconds=data["msPlayed"]),
        )

    def to_timezone(self, timezone: zoneinfo.ZoneInfo) -> "Track":
        return Track(
            artist=self.artist,
            track=self.track,
            start=self.start.replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(timezone),
            end=self.end.replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(timezone),
            duration=self.duration,
        )
