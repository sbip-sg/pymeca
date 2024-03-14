# read version from installed package
from importlib.metadata import version
__version__ = version("pymeca")

__author__ = "Stefan-Dan Ciocirlan (sdcioc)"
__copyright__ = "Copyright 2023, Singapore Blockchain Innovation Programme"
__credits__ = []
__license__ = "MIT"
__maintainer__ = "Stefan-Dan Ciocirlan"
__email__ = "stefan_dan@xn--ciocrlan-o2a.ro"

from . import dao as dao
from . import pymeca as pymeca
from . import utils as utils
from . import host as host
from . import task as task
from . import tower as tower
from . import user as user

__all__ = [
    "dao",
    "pymeca",
    "utils",
    "host",
    "task",
    "tower",
    "user"
]
