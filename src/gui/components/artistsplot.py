from typing import Iterable, List

import matplotobjlib as plot

import utils
from gui.components import PlotComponent
from gui.options import ArtistChooser, Spinbox
from track import Track


class ArtistsPlot(PlotComponent):
    name = "Listens Per Day"
    options = [ArtistChooser, Spinbox(text="Moving average days: ", from_=1, to=14, default=7)]

    def subplot(self, all_tracks: List[Track], artists: List[str], smoothing: int) -> plot.SubPlot:  # type: ignore # pylint: disable=arguments-differ
        days, listens_per_day = utils.listens_per_day(all_tracks)

        return plot.SubPlot(
            *(
                plot.Graph(
                    x_values=days,
                    y_values=utils.moving_average(listens_per_day[artist], smoothing),
                    legend_label=artist,
                    plot_type="-",
                )
                for artist in artists
            )
        )
