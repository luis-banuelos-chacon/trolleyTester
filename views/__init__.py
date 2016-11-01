# UI File Importer
from PyQt4 import uic
from glob import glob
from os.path import split, join

# Stores all loaded UI classes by name
View = {}

# Load UI files
path = split(__file__)[0]
for ui in glob(join(path, '*.ui')):
    base, form = uic.loadUiType(ui)

    # get name in CamelCase
    name = split(ui)[1][:-3]
    name = name.title().replace(' ', '').replace('_', '')

    View[name] = type(name, (base, form), {})

# Import classes
from .program_tab import ProgramTab
from .connection_tab import ConnectionTab
from .axis_manual_control import AxisManualControl
