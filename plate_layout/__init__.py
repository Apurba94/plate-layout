"""Design multi-well plate layouts with replicates and controls."""
from .core import Plate, FORMATS, well_name, parse_well

__version__ = "0.1.0"
__all__ = ["Plate", "FORMATS", "well_name", "parse_well"]
