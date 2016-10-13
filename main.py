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
        log.getLogger().setLevel(log.DEBUG)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


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
        self.mainBox.setTitle(self._axis.name)
        self.setup()

    def setup(self):
        '''Binds UI controls to axis.'''
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

        # tool box changed
        self.toolBox.currentChanged.connect(self.toolBoxChanged)

    def toolBoxChanged(self, index):
        if self.toolBox.currentWidget() is self.configurationWidget:
            self.accelerationSpinBox.setValue(int(self._axis.acceleration))
            self.decelerationSpinBox.setValue(int(self._axis.deceleration))
            self.torqueLimitSpinBox.setValue(int(self._axis.torque_limit))

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
        speed = float(self.speedSpinBox.value())
        time = float(self.timeSpinBox.value())
        delta = speed * (time / 1000)

        if direction == '-':
            delta *= -1

        self._axis.position_relative = delta
        self._axis.speed = speed
        self._axis.begin()

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
        self._axis.disable()

    def setJogSpeed(self, speed):
        '''Sets new jog speed on the fly.'''
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

        # Axis
        self.axis_left = []
        self.axis_left.append(GalilAxis('A', self.galil[0], 'Hopper Shaker'))
        self.axis_left.append(GalilAxis('B', self.galil[0], 'Trough Shaker'))
        self.axis_left.append(GalilAxis('A', self.galil[1], 'Lifter Motor'))
        self.axis_right = []
        self.axis_right.append(GalilAxis('E', self.galil[0], 'Hopper Shaker'))
        self.axis_right.append(GalilAxis('F', self.galil[0], 'Trough Shaker'))
        self.axis_right.append(GalilAxis('B', self.galil[1], 'Lifter Motor'))

        # setup logging window
        QLogger(self.logView)

    def setupFrontend(self):
        # Connection Tab
        self.connectionTab = ConnectionTab(self.galil, self)
        self.tabWidget.addTab(self.connectionTab, 'Connection')

        # Left Tab
        self.leftLayout = QtGui.QHBoxLayout()
        self.leftTab = QtGui.QWidget()
        for axis in self.axis_left:
            self.leftLayout.addWidget(AxisManualControl(axis))
        self.leftTab.setLayout(self.leftLayout)
        self.tabWidget.addTab(self.leftTab, 'Left')

        # Right Tab
        self.rightLayout = QtGui.QHBoxLayout()
        self.rightTab = QtGui.QWidget()
        for axis in self.axis_right:
            self.rightLayout.addWidget(AxisManualControl(axis))
        self.rightTab.setLayout(self.rightLayout)
        self.tabWidget.addTab(self.rightTab, 'Right')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
