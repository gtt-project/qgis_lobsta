import os
import sys
from qgis.gui import QgisInterface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lobsta import Lobsta

__author__ = "Taro Matsuzawa"
__date__ = "2025-03-11"
__copyright__ = "Copyright 2025 Georepublic"

# to import modules as non-relative
sys.path.append(os.path.dirname(__file__))


def classFactory(iface: QgisInterface) -> "Lobsta":
    """Load Lobsta class from file lobsta.py."""
    from .lobsta import Lobsta

    return Lobsta(iface)
