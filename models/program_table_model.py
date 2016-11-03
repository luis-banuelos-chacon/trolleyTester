from PyQt4 import QtCore, QtGui


class ProgramTableModel(QtCore.QAbstractTableModel):

    def __init__(self, axes, parent=None):
        super(ProgramTableModel, self).__init__(parent)

        self._headers = ['Time', 'Axis', 'Action', 'Speed', 'Duration']
        self._keys = ['time', 'axis', 'action', 'speed', 'duration']
        self._data = []

        self._axes = axes

        self._data = sorted(self._data, key=lambda k: k['time'])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return ' {} '.format(section)

    def rowCount(self, parent):
        if parent.isValid():
            return 0

        return len(self._data)

    def columnCount(self, parent):
        if parent.isValid():
            return 0

        return len(self._headers)

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def data(self, index, role):
        column = index.column()
        row = index.row()
        key = self._keys[column]
        value = self._data[row][key]

        if role == QtCore.Qt.DisplayRole:
            if key in ['time', 'duration']:
                return '{} ms'.format(value)

            if key == 'speed':
                return '{} rev/s'.format(value)

            if key == 'axis':
                return value.name

            else:
                return value

        if role == QtCore.Qt.EditRole:
            if key == 'axis':
                return value.name

            else:
                return value

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.EditRole:
            self._data[row][self._keys[column]] = value
            self.sortData()
            self.dataChanged.emit(index, index)
            return True

        return False

    def sortData(self):
        self._data = sorted(self._data, key=lambda k: k['time'])

    def insertRow(self, row, parent=None):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self._data.insert(row, {'time': 0, 'axis': self._axes[0], 'action': 'timed move', 'speed': 0, 'duration': 0})
        self.sortData()
        self.endInsertRows()

    def removeRow(self, row, parent=None):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self._data.pop(row)
        self.endRemoveRows()

    class ItemDelegate(QtGui.QStyledItemDelegate):

        def createEditor(self, parent, option, index):
            model = index.model()
            column = index.column()
            axes = model._axes
            key = model._keys[column]

            if key in ['time', 'speed', 'duration']:
                editor = QtGui.QSpinBox(parent)

                if key in ['time', 'duration']:
                    editor.setSuffix(' ms')
                    editor.setRange(0, 1000000)
                    editor.setSingleStep(10)
                if key == 'speed':
                    editor.setSuffix(' rev/s')
                    editor.setRange(-1000000, 1000000)
                    editor.setSingleStep(1)

            elif key == 'axis':
                editor = QtGui.QComboBox(parent)
                for axis in axes:
                    editor.addItem(axis.name)

            elif key == 'action':
                editor = QtGui.QComboBox(parent)
                editor.addItem('timed move')
                editor.addItem('jog move')
                editor.addItem('stop')

            else:
                editor = super(ProgramTableModel.ItemDelegate, self).createEditor(parent, option, index)

            return editor

        def setModelData(self, editor, model, index):
            column = index.column()
            axes = model._axes
            key = model._keys[column]

            if key in ['time', 'speed', 'duration']:
                model.setData(index, editor.value())

            elif key == 'axis':
                axis = axes[editor.currentIndex()]
                model.setData(index, axis)

            elif key == 'action':
                model.setData(index, editor.currentText())

            else:
                super(ProgramTableModel.ItemDelegate, self).setModelData(editor, model, index)
