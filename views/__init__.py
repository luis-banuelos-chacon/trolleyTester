# UI File Importer
from PyQt4 import uic
from glob import glob
from os.path import dirname, basename, join

# Stores all loaded UI classes by name
View = {}

# Load UI files
path = dirname(__file__)
for ui in glob(join(path, '*.ui')):
    base, form = uic.loadUiType(ui)

    # get name in CamelCase
    name = basename(ui)[:-3]
    name = name.title().replace(' ', '').replace('_', '')

    View[name] = type(name, (base, form), {})

# Import classes
from .program_tab import ProgramTab
from .connection_tab import ConnectionTab
from .axis_simple import AxisSimple
from .axis_two_state import AxisTwoState
