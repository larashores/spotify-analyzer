import collections
import datetime
from typing import Dict, Iterable, List, Set, Tuple

import matplotobjlib as plot

import utils
from gui.components import PlotComponent
from gui.options import ArtistChooser, CheckButton
from track import Track


class ArtistsPlot(PlotComponent):
    name = "Listens per day (7 day average)"
    options = [ArtistChooser]

    def graphs(self, all_tracks: List[Track], artists: List[str]) -> Iterable[plot.Graph]:  # type: ignore # pylint: disable=arguments-differ
        days, listens_per_day = utils.listens_per_day(all_tracks)

        return (
            plot.Graph(
                x_values=days,
                y_values=utils.moving_average(listens_per_day[artist], 7),
                legend_label=artist,
                plot_type="-",
            )
            for artist in artists
        )
