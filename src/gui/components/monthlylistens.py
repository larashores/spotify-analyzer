import calendar
import collections
import datetime
from typing import Dict, List

import utils
from gui.components import TextComponent
from track import Track


class MonthlyListens(TextComponent):
    name = "Monthly Listens"

    def text(self, tracks: List[Track]) -> str:  # type: ignore # pylint: disable=arguments-differ
        months_to_tracks: Dict[datetime.date, List[Track]] = collections.defaultdict(list)
        for track in tracks:
            months_to_tracks[utils.in_month(track)].append(track)
        months = sorted(months_to_tracks.items(), key=lambda item: item[0], reverse=True)

        month_table = []
        for date, months_tracks in months:
            duration = sum((track.duration for track in months_tracks), datetime.timedelta())
            hours, minutes, _ = utils.hours_minutes_seconds(duration)
            month_str = f"{calendar.month_name[date.month]} {date.year:d}:"
            month_table.append((month_str, f"{hours} hours", f"{minutes} minutes"))

        return utils.pformat_table(month_table, justify="<", sep=" ")
