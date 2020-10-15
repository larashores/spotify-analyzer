import collections
import datetime
from typing import Dict, List

import utils
from gui.components import TextComponent
from track import Track


class TopArtistsByListens(TextComponent):
    name = "Top Artists by Listens"

    def text(self, tracks: List[Track]) -> str:  # type: ignore # pylint: disable=arguments-differ
        artists_to_tracks: Dict[str, List[Track]] = collections.defaultdict(list)
        for track in tracks:
            artists_to_tracks[track.artist].append(track)

        top_artists = sorted(artists_to_tracks.items(), key=lambda item: len(item[1]), reverse=True)
        return utils.pformat_table(
            ((artist + ":", len(tracks)) for artist, tracks in top_artists[:20]), justify="<", sep=" "
        )


class TopArtistsByDuration(TextComponent):
    name = "Top Artists by Listen Duration"

    def text(self, tracks: List[Track]) -> str:  # type: ignore # pylint: disable=arguments-differ
        artist_to_duration: Dict[str, datetime.timedelta] = collections.defaultdict(datetime.timedelta)
        for track in tracks:
            artist_to_duration[track.artist] += track.duration
        top_artists = sorted(artist_to_duration.items(), key=lambda item: item[1], reverse=True)

        duration_table = []
        for artist, duration in top_artists[:20]:
            hours, minutes, _ = utils.hours_minutes_seconds(duration)
            duration_table.append((artist + ":", f"{hours} hours", f"{minutes} minutes"))
        return utils.pformat_table(duration_table, justify="<", sep=" ")
