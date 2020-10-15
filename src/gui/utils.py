import dataclasses
import importlib
import json
import logging
import os
import re
from typing import List, Set, Type

from gui.components import Component
from track import Track

logger = logging.getLogger(f"analysis.{__name__}")


def load_components(path: str) -> List[Type[Component]]:
    components: List[Type[Component]] = []
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        module_name = f"components.{name}"
        if os.path.isfile(full_path) and name.endswith(".py"):
            try:
                spec = importlib.util.spec_from_file_location(module_name, full_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
            except:  # pylint: disable=bare-except
                logger.exception("Error loading module %r:", name)
            components.extend(
                obj
                for obj in (getattr(module, name) for name in dir(module))
                if isinstance(obj, type) and issubclass(obj, Component) and obj.__module__ == module_name
            )
    return components


@dataclasses.dataclass
class LoadTracksResult:
    tracks: List[Track]
    errors: List[str]


def load_tracks(path: str) -> LoadTracksResult:
    errors: List[str] = []
    tracks: Set[Track] = set()
    for root, _, files in os.walk(path):
        for file_name in files:
            if re.match("StreamingHistory[0-9]*.json", file_name):
                try:
                    with open(os.path.join(root, file_name), "rb") as file:
                        data = file.read()
                    decoded = json.loads(data)
                except:  # pylint: disable=bare-except
                    logger.exception("Error loading tracks file %r", file_name)
                    errors.append(file_name)
                tracks.update(Track.from_json(obj) for obj in decoded)
    return LoadTracksResult(sorted(tracks, key=lambda item: item.start), errors)
