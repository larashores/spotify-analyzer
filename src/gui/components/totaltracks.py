from typing import List

from gui.components import TextComponent
from track import Track


class TotalTracks(TextComponent):
    name = "Total Tracks"

    def text(self, tracks: List[Track]) -> str:  # type: ignore # pylint: disable=arguments-differ
        return f"{len(tracks):,d} tracks listened to between {tracks[0].start.date()} and {tracks[-1].end.date()}"
