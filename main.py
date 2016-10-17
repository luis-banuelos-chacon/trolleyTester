from PyQt4 import QtGui, QtCore
from views import ViewBase, ViewForm
from modules import GalilController, GalilAxis
import logging as log
import sys


class QLogger(log.Handler):
    def __init__(self, widget):
        super(QLogger, self).__init__()

        self.widget = widget
        self.widget.setReadOnly(True)

        self.setFormatter(log.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        log.getLogger().addHandler(self)
        log.getLogger().setLevel(log.INFO)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


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
                return '{} ct/s'.format(value)

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
                editor.setRange(0, 1000000)
                editor.setSingleStep(100)
                if key in ['time', 'duration']:
                    editor.setSuffix(' ms')
                if key == 'speed':
                    editor.setSuffix(' ct/s')

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


class ProgramTab(ViewBase['ProgramTab'], ViewForm['ProgramTab']):

    def __init__(self, axes, parent=None):
        super(ViewBase['ProgramTab'], self).__init__(parent)
        self.setupUi(self)

        self._axes = axes

        self.model = ProgramTableModel(axes)

        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.setItemDelegate(self.model.ItemDelegate())

        self.addButton.clicked.connect(self.add)
        self.removeButton.clicked.connect(self.remove)

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
        pass

    def execute(self):
        data = self.model._data
        time = 0

        while True:
            for item in data:
                if item['time'] == time:
                    action = item['action']
                    axis = item['axis']
                    speed = item['speed']
                    duration = item['duration']

                    if action == 'timed move':
                        axis.jog_speed = speed
                        axis.enable()
                        axis.begin()




    def stop(self):
        pass

class ConnectionTab(ViewBase['ConnectionTab'], ViewForm['ConnectionTab']):

    def __init__(self, galil, parent=None):
        super(ViewBase['ConnectionTab'], self).__init__(parent)
        self.setupUi(self)

        # get reference to galil controllers
        self.galil = galil

        # widgets into lists
        self.address = []
        self.address.append(self.address_0)
        self.address.append(self.address_1)
        self.connect_btn = []
        self.connect_btn.append(self.connect_0)
        self.connect_btn.append(self.connect_1)

        # connect signals
        self.connect_btn[0].clicked.connect(lambda v, i=0: self.connect(i))
        self.connect_btn[1].clicked.connect(lambda v, i=1: self.connect(i))

    def connect(self, id):
        if self.galil[id].connected:
            # disconnect
            self.galil[id].close()
            self.connect_btn[id].setText('Connect')

        else:
            # connect
            self.connect_btn[id].setDown(True)

            if self.galil[id].open(str(self.address[id].text())):
                self.connect_btn[id].setText('Disconnect')
            else:
                self.connect_btn[id].setText('Connect')

            self.connect_btn[id].setDown(False)


class AxisManualControl(ViewBase['AxisManualControl'], ViewForm['AxisManualControl']):

    _refresh_rate = 100

    def __init__(self, axis, parent=None):
        super(ViewBase['AxisManualControl'], self).__init__(parent)
        self.setupUi(self)

        self._axis = axis

        # set name
        self.mainBox.setTitle(self._axis.name)

        # timed
        self.timedPlusButton.clicked.connect(lambda x: self.timed('+'))
        self.timedMinusButton.clicked.connect(lambda x: self.timed('-'))

        # jog
        self.jogPlusButton.clicked.connect(lambda x: self.jog('+'))
        self.jogMinusButton.clicked.connect(lambda x: self.jog('-'))
        self.jogSpeedSpinBox.valueChanged.connect(self.setJogSpeed)

        # configuration
        self.accelerationSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('acceleration', v))
        self.decelerationSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('deceleration', v))
        self.torqueLimitSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('torque_limit', v))

        # stop
        self.stopButton.clicked.connect(self.stop)

        # data polling
        self._autoRefresh = QtCore.QTimer(self)
        self._autoRefresh.timeout.connect(self.refresh)

        # timer
        self._stopTimer = QtCore.QTimer(self)
        self._stopTimer.setSingleShot(True)
        self._stopTimer.timeout.connect(self.stop)

        # tool box changed
        self.toolBox.currentChanged.connect(self.toolBoxChanged)

    def toolBoxChanged(self, index):
        if self.toolBox.currentWidget() is self.configurationWidget:
            self.accelerationSpinBox.setValue(int(self._axis.acceleration))
            self.decelerationSpinBox.setValue(int(self._axis.deceleration))
            self.torqueLimitSpinBox.setValue(float(self._axis.torque_limit))

    def showEvent(self, event):
        super(ViewBase['AxisManualControl'], self).showEvent(event)
        self._autoRefresh.start(self._refresh_rate)

    def hideEvent(self, event):
        super(ViewBase['AxisManualControl'], self).hideEvent(event)
        self._autoRefresh.stop()

    def refresh(self):
        '''Updates all views with data from controller.'''
        # information
        if self.toolBox.currentWidget() is self.informationWidget:
            self.positionEdit.setText(str(self._axis.position))
            self.velocityEdit.setText(str(self._axis.velocity))
            self.torqueEdit.setText(str(self._axis.torque))
            self.errorEdit.setText(str(self._axis.error))

    def timed(self, direction='+'):
        '''Moves for a specified time at speed.'''
        jog_speed = float(self.speedSpinBox.value())
        time = float(self.timeSpinBox.value())

        if direction == '-':
            jog_speed *= -1

        self._axis.jog = jog_speed
        self._axis.enable()
        self._axis.begin()
        self._stopTimer.start(time)

    def jog(self, direction='+'):
        '''Moves indefinitely at jog speed.'''
        jog_speed = float(self.jogSpeedSpinBox.value())

        if direction == '-':
            jog_speed *= -1

        self._axis.jog = jog_speed
        self._axis.enable()
        self._axis.begin()

    def stop(self):
        '''Stops the current move.'''
        self._axis.stop()
        self._axis.wait()
        self._axis.disable()

    def setJogSpeed(self, speed):
        '''Sets new jog speed on the fly.'''
        print(self._axis.jog)
        if self._axis.jog >= 0:
            self._axis.jog = speed
        else:
            self._axis.jog = (speed * -1)


class MainWindow(ViewBase['MainWindow'], ViewForm['MainWindow']):

    def __init__(self, parent=None):
        super(ViewBase['MainWindow'], self).__init__(parent)
        self.setupUi(self)

        self.setupBackend()
        self.setupFrontend()

    def setupBackend(self):
        # Galil Controllers
        self.galil = []
        self.galil.append(GalilController('Galil 0 - 24V'))
        self.galil.append(GalilController('Galil 1 - 48V'))

        # self.axis = GalilAxis('X', self.galil[0])

        # Axis
        self.axes = []
        self.axes.append(GalilAxis('A', self.galil[0], 'Hopper Shaker (Back)'))
        self.axes.append(GalilAxis('B', self.galil[0], 'Trough Shaker (Back)'))
        self.axes.append(GalilAxis('A', self.galil[1], 'Lifter Motor (Back)'))
        self.axes.append(GalilAxis('E', self.galil[0], 'Hopper Shaker (Front)'))
        self.axes.append(GalilAxis('F', self.galil[0], 'Trough Shaker (Front)'))
        self.axes.append(GalilAxis('B', self.galil[1], 'Lifter Motor (Front)'))

        # setup logging window
        QLogger(self.logView)

    def setupFrontend(self):
        # Connection Tab
        self.connectionTab = ConnectionTab(self.galil, self)
        self.tabWidget.addTab(self.connectionTab, 'Connection')

        # self.testTab = AxisManualControl(self.axis, self)
        # self.tabWidget.addTab(self.testTab, 'Test')

        # Autofill Axis
        layout = QtGui.QHBoxLayout()
        for i, axis in enumerate(self.axes):
            layout.addWidget(AxisManualControl(axis))

            if i % 3 >= 2 or i == len(self.axes) - 1:
                tab = QtGui.QWidget()
                tab.setLayout(layout)
                self.tabWidget.addTab(tab, 'Page ' + str(i / 3))
                layout = QtGui.QHBoxLayout()

        # Program Tab
        self.programTab = ProgramTab(self.axes, self)
        self.tabWidget.addTab(self.programTab, 'Program')



        # Left Tab
        # self.leftLayout = QtGui.QHBoxLayout()
        # self.leftTab = QtGui.QWidget()
        # for axis in self.axis[3:]:
        #     self.leftLayout.addWidget(AxisManualControl(axis))
        # self.leftTab.setLayout(self.leftLayout)
        # self.tabWidget.addTab(self.leftTab, 'Left')

        # # Right Tab
        # self.rightLayout = QtGui.QHBoxLayout()
        # self.rightTab = QtGui.QWidget()
        # for axis in self.axis[:3]:
        #     self.rightLayout.addWidget(AxisManualControl(axis))
        # self.rightTab.setLayout(self.rightLayout)
        # self.tabWidget.addTab(self.rightTab, 'Right')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
