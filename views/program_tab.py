from PyQt4 import QtGui, uic
from models import ProgramTableModel
from modules import ProgramThread
from . import View


class ProgramTab(View['ProgramTab']):

    def __init__(self, axes, parent=None):
        super(ProgramTab, self).__init__(parent)
        self.setupUi(self)

        self.axes = axes

        self.model = ProgramTableModel(axes)

        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.setItemDelegate(self.model.ItemDelegate())
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged | QtGui.QAbstractItemView.SelectedClicked)

        self.addButton.clicked.connect(self.add)
        self.removeButton.clicked.connect(self.remove)
        self.sortButton.clicked.connect(self.sort)

        self.loadButton.clicked.connect(self.load)
        self.saveButton.clicked.connect(self.save)

        self.runButton.clicked.connect(self.run)
        self.stopButton.clicked.connect(self.stop)

        self.loopSpinBox.setSpecialValueText(u"\u221E")

        self.worker = None

    def load(self):
        path = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', 'JSON Files (*.json)')
        try:
            self.model.loadJSON(path)
        except IOError:
            pass

    def save(self):
        path = QtGui.QFileDialog.getSaveFileName(self, 'Save File', 'recipe.json', 'JSON Files (*.json)')
        try:
            self.model.saveJSON(path)
        except IOError:
            pass

    def add(self):
        index = self.tableView.selectionModel().currentIndex()

        if index.isValid():
            row = index.row()
        else:
            row = 0

        self.model.insertRow(row + 1)

    def remove(self):
        index = self.tableView.selectionModel().currentIndex()

        if index.isValid():
            self.model.removeRow(index.row())

    def sort(self):
        self.model.sort()

    def run(self):
        loops = self.loopSpinBox.value()
        self.worker = ProgramThread(self.axes, self.model.program, loops, self)
        self.worker.started.connect(self.programStarted)
        self.worker.instruction_changed.connect(self.highlightInstruction)
        self.worker.iteration_changed.connect(self.loopSpinBox.setValue)
        self.worker.finished.connect(self.programFinished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()

    def programStarted(self):
        self.runButton.setText("RUNNING")
        self.runButton.setEnabled(False)

    def programFinished(self):
        self.runButton.setText("RUN")
        self.runButton.setEnabled(True)
        self.worker = None

    def highlightInstruction(self, row):
        self.tableView.selectRow(row)
