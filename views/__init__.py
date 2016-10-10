from PyQt4 import uic
from glob import glob
from os.path import split, join

# Stores all loaded UI classes by name
ViewBase = {}
ViewForm = {}

# Load UI files
path = split(__file__)[0]
for ui in glob(join(path, '*.ui')):
    base, form = uic.loadUiType(ui)
    name = split(ui)[1][:-3]

    ViewBase[name] = base
    ViewForm[name] = form
