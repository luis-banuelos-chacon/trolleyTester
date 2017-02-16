from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import json


class ProgramTableModel(QtCore.QAbstractTableModel):

    Qt.TagRole      = Qt.UserRole
    Qt.DefaultRole  = Qt.UserRole + 1
    Qt.TypeRole     = Qt.UserRole + 2

    Qt.SuffixRole   = Qt.UserRole + 3
    Qt.RangeRole    = Qt.UserRole + 4
    Qt.StepRole     = Qt.UserRole + 5
    Qt.ListRole     = Qt.UserRole + 6

    def __init__(self, axes, parent=None):
        super(ProgramTableModel, self).__init__(parent)

        self.axes = axes

        self.headers = ['Time', 'Axis', 'Action', '', '', '']
        self.keys = ['time', 'axis', 'action', 'arg', 'arg', 'arg']

        self.actions = {
            'Timed': [
                {
                    'tag': 'Speed',
                    'default': 1,
                    'type': 'integer',
                    'suffix': 'rev/s',
                    'step': 1
                },
                {
                    'tag': 'Duration',
                    'default': 100,
                    'type': 'integer',
                    'suffix': 'ms',
                    'step': 100
                }
            ],
            'Range': [
                {
                    'tag': 'Speed',
                    'default': 1,
                    'type': 'integer',
                    'suffix': 'rev/s',
                    'step': 1
                },
                {
                    'tag': 'Position',
                    'default': 50,
                    'type': 'integer',
                    'suffix': '%',
                    'step': 1
                }
            ],
            'PingPong': [
                {
                    'tag': 'Speed',
                    'default': 1,
                    'type': 'integer',
                    'suffix': 'rev/s',
                    'step': 1
                },
                {
                    'tag': 'Stroke',
                    'default': 50,
                    'type': 'integer',
                    'suffix': '%',
                    'step': 1
                },
                {
                    'tag': 'Repeats',
                    'default': 1,
                    'type': 'integer',
                    'suffix': '',
                    'step': 1
                }
            ]
        }

        self.columns = {
            'time': {
                'default': 0,
                'type': 'integer',
                'suffix': 'ms',
                'step': 1
            },
            'axis': {
                'default': 0,
                'type': 'list',
                'list': self.axes.keys()
            },
            'action': {
                'default': self.actions.keys()[0],
                'type': 'list',
                'list': self.actions.keys()
            }
        }

        self.program = []

    def loadJSON(self, path):
        with open(path, 'r') as f:
            self.program = json.load(f)
            self.sort()

    def saveJSON(self, path):
        with open(path, 'w') as f:
            json.dump(self.program, f)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    num = section - len(self.headers)
                    return 'Param {}'.format(num)

            else:
                return ' {} '.format(section)

    def rowCount(self, parent):
        if parent.isValid():
            return 0

        return len(self.program)

    def columnCount(self, parent):
        if parent.isValid():
            return 0

        return len(self.headers)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role):
        col = index.column()
        row = index.row()
        key = self.keys[col]
        task = self.program[row]

        # get the value
        if key == 'arg':
            try:
                value = task['args'][col-3]
            except:
                value = ''

            try:
                meta = self.actions[task['action']][col-3]
            except:
                meta = {}

        else:
            value = task[key]
            meta = self.columns[key]

        # return the value
        if role in [Qt.DisplayRole, Qt.EditRole]:
            return value

        # return metadata
        if role == Qt.TypeRole and 'type' in meta:
            return meta['type']

        if role == Qt.DefaultRole and 'default' in meta:
            return meta['default']

        if role == Qt.TagRole and 'tag' in meta:
            return meta['tag']

        if role == Qt.SuffixRole and 'suffix' in meta:
            return meta['suffix']

        if role == Qt.StepRole and 'step' in meta:
            return meta['step']

        if role == Qt.ListRole and 'list' in meta:
            return meta['list']

        return QtCore.QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        col = index.column()
        row = index.row()
        key = self.keys[col]
        task = self.program[row]

        if role == Qt.EditRole:
            if key == 'arg':
                task['args'][col-3] = value
                self.dataChanged.emit(index, index)

            elif key == 'action':
                # set default variables for params
                task['args'] = [0 for item in self.actions[str(value)]]
                for idx, meta in enumerate(self.actions[str(value)]):
                    task['args'][idx] = meta['default']

                # set action
                task[key] = str(value)
                self.dataChanged.emit(index, self.createIndex(row, 5))

            elif key == 'axis':
                task[key] = str(value)
                self.dataChanged.emit(index, index)

            else:
                task[key] = value
                self.dataChanged.emit(index, index)

            return True

        return False

    def sort(self):
        self.layoutAboutToBeChanged.emit()
        self.program = sorted(self.program, key=lambda k: k['time'])
        self.layoutChanged.emit()

    def insertRow(self, row, parent=None):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)

        task = {
            'time': 0,
            'axis': self.axes.keys()[0],
            'action': self.actions.keys()[0],
            'args': [0 for arg in self.actions.items()[0]]
        }

        self.program.insert(row, task)
        self.endInsertRows()

    def removeRow(self, row, parent=None):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self.program.pop(row)
        self.endRemoveRows()

    class ItemDelegate(QtGui.QStyledItemDelegate):

        def createEditor(self, parent, option, index):
            typ = index.data(Qt.TypeRole).toPyObject()
            val = index.data(Qt.EditRole).toPyObject()

            if typ == None:
                editor = QtGui.QWidget(parent)

            elif typ == 'integer':
                editor = QtGui.QSpinBox(parent)
                suffix = index.data(Qt.SuffixRole).toPyObject()
                step = index.data(Qt.StepRole).toPyObject()
                rng = index.data(Qt.RangeRole).toPyObject()

                if suffix:
                    editor.setSuffix(' ' + suffix)

                if step:
                    editor.setSingleStep(step)

                if rng:
                    editor.setRange(rng[0], rng[1])
                else:
                    editor.setRange(-1000000, 1000000)

                editor.setValue(val)

            elif typ == 'list':
                editor = QtGui.QComboBox(parent)
                lst = index.data(Qt.ListRole).toPyObject()
                for item in lst:
                    editor.addItem(item)

            return editor

        def setModelData(self, editor, model, index):
            typ = index.data(Qt.TypeRole).toPyObject()

            if typ == None:
                return

            if typ == 'integer':
                model.setData(index, editor.value())

            elif typ == 'list':
                model.setData(index, editor.currentText())

            else:
                super(ProgramTableModel.ItemDelegate, self).setModelData(editor, model, index)

        def paint(self, painter, option, index):
            self.initStyleOption(option, index)
            painter.save()

            val = index.data(Qt.EditRole).toPyObject()
            tag = index.data(Qt.TagRole).toPyObject()
            suffix = index.data(Qt.SuffixRole).toPyObject()
            string = ''

            if tag:
                string += '{}\n'.format(tag)

            string += str(val)

            if suffix:
                string += ' {}'.format(suffix)

            painter.drawText(option.rect, Qt.AlignCenter, string)
            painter.restore()
