import collections
import datetime
from typing import Dict, Iterable, List, Set, Tuple

import matplotobjlib as plot

import utils
from gui.components import PlotComponent
from gui.options import CheckButton
from track import Track


class ArtistsPlot(PlotComponent):
    name = "Peak Artists by Listens"
    options = [CheckButton("Exclude Watsky")]

    def graphs(  # type: ignore # pylint: disable=arguments-differ
        self, all_tracks: List[Track], exclude_watsky: bool
    ) -> Iterable[plot.Graph]:
        tracks_by_day: Dict[datetime.date, List[Track]] = collections.defaultdict(list)
        for track in all_tracks:
            tracks_by_day[utils.in_day(track)].append(track)

        all_artists: Set[str] = set(track.artist for track in all_tracks)
        daily_tracks: List[Tuple[datetime.date, List[Track]]] = sorted(tracks_by_day.items(), key=lambda item: item[0])
        listens_per_day: Dict[str, List[int]] = collections.defaultdict(list)

        for _day, tracks in daily_tracks:
            artist_to_tracks: Dict[str, List[Track]] = collections.defaultdict(list)
            for track in tracks:
                artist_to_tracks[track.artist].append(track)

            for artist in all_artists:
                listens_per_day[artist].append(len(artist_to_tracks[artist]))

        max_peaks = {artist: max(listens) for artist, listens in listens_per_day.items()}

        display_artists = [
            item[0]
            for item in sorted(
                max_peaks.items(),
                key=lambda item: (item[1] if not exclude_watsky or item[0] != "Watsky" else 0),
                reverse=True,
            )[:10]
        ]

        days = list(tracks_by_day.keys())
        return (
            plot.Graph(
                x_values=days,
                y_values=utils.moving_average(listens_per_day[artist], 7),
                legend_label=artist,
                plot_type="-",
            )
            for artist in display_artists
        )
