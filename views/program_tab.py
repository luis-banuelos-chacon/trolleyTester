from PyQt4 import QtGui, uic
from models import ProgramTableModel
from modules import ProgramThread
from . import View


class ProgramTab(View['ProgramTab']):

    def __init__(self, axes, parent=None):
        super(ProgramTab, self).__init__(parent)
        self.setupUi(self)

        self._axes = axes

        self.model = ProgramTableModel(axes)

        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.setItemDelegate(self.model.ItemDelegate())

        self.addButton.clicked.connect(self.add)
        self.removeButton.clicked.connect(self.remove)

        self.runButton.clicked.connect(self.run)
        self.stopButton.clicked.connect(self.stop)

        self.loopBox.stateChanged.connect(self.setLoop)

        self._worker = None

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

    def run(self):
        self._worker = ProgramThread(self.model._data, self)
        self._worker.started.connect(self.programStarted)
        self._worker.instruction_changed.connect(self.highlightInstruction)
        self._worker.finished.connect(self.programFinished)
        self._worker.finished.connect(self._worker.deleteLater)
        if self.loopBox.isChecked():
            self._worker.loop = True
        self._worker.start()

    def setLoop(self, enable):
        if self._worker:
            if enable:
                self._worker.loop = True
            else:
                self._worker.loop = False

    def stop(self):
        if self._worker:
            self._worker.stop()

    def programStarted(self):
        self.runButton.setText("RUNNING")
        self.runButton.setEnabled(False)

    def programFinished(self):
        self.runButton.setText("RUN")
        self.runButton.setEnabled(True)
        self._worker = None

    def highlightInstruction(self, row):
        self.tableView.selectRow(row)
