import collections
import colorsys
from typing import Iterable, List, Tuple

import matplotobjlib as plot
from backports import zoneinfo
from matplotlib.colors import ListedColormap

import utils
from gui.components import PlotComponent
from gui.options import ArtistChooser, Spinbox
from track import Track


def _colormap(hue: float) -> ListedColormap:
    return ListedColormap([colorsys.hsv_to_rgb(hue, saturation / 255, 1) for saturation in range(255)])


class WeeklyColorMesh(PlotComponent):
    name = "Weekly Color Mesh"
    adjust = plot.SubplotsAdjust(left=0.08, right=0.975, top=0.975, bottom=0.09)

    def subplot(self, tracks: List[Track]) -> plot.SubPlot:  # type: ignore # pylint: disable=arguments-differ

        values = [[0 for i in range(24)] for i in range(7)]
        for track in tracks:
            track = track.to_timezone(zoneinfo.ZoneInfo("America/Los_Angeles"))
            values[-((utils.in_day(track).weekday() - 5)) % 7][utils.in_hour(track).hour - 1] += 1

        return plot.SubPlot(
            plot.Colormesh(values, _colormap(240 / 360)),
            x_tick_options=plot.TickOptions(
                labels=[f"{i+1}\nam" for i in range(11)] + ["12\npm"] + [f"{i+1}\npm" for i in range(11)] + ["12\nam"],
                values=[i + 0.5 for i in range(24)],
            ),
            y_tick_options=plot.TickOptions(
                labels=["Saturday", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday", "Sunday"],
                values=[i + 0.5 for i in range(7)],
            ),
        )
