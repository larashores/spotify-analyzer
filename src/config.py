import dataclasses
import logging
from typing import Optional

import toml

logger = logging.getLogger(f"analyzer.{__name__}")


@dataclasses.dataclass
class Config:
    component_directory: Optional[str] = None
    enable_logs: Optional[bool] = False

    @classmethod
    def load(cls, path: str) -> "Config":
        kwargs = {}
        try:
            values = toml.load(path)
        except FileNotFoundError:
            logger.warning("TOML config %r not found", path)
        except toml.TomlDecodeError:
            logger.exception("Error loading TOML config %r", path)
        else:
            for key, value in values.items():
                if key in cls.__dataclass_fields__:  # type: ignore # pylint: disable=no-member
                    kwargs[key] = value
        return Config(**kwargs)
