from PyQt4 import QtCore
from threading import Thread
from . import View
import time


class AxisTwoState(View['AxisTwoState']):

    _refresh_rate = 500

    def __init__(self, axis, name, parent=None):
        super(AxisTwoState, self).__init__(parent)
        self.setupUi(self)

        # controller
        self._axis = axis

        # set name
        self.name = name
        self.mainBox.setTitle(self.name)

        # settings
        self.readSettings()

        # motion
        self.goButton.clicked.connect(self.go)
        self.centerButton.clicked.connect(self.center)
        self.rightButton.clicked.connect(self.right)
        self.leftButton.clicked.connect(self.left)

        # configuration
        self.homeButton.clicked.connect(self.home)
        self.convFactorSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('conversion_factor', v))
        self.limitSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('home_limit', v))

        # stop
        self.stopButton.clicked.connect(self._axis.cancel)

        # data polling
        self._autoRefresh = QtCore.QTimer(self)
        self._autoRefresh.timeout.connect(self.refresh)

        # tool box changed
        self.toolBox.currentChanged.connect(self.toolBoxChanged)
        self.toolBoxChanged(False)

        # connect window closing event
        if parent:
            parent.closing.connect(self.writeSettings)

    def readSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup(self.name)
        self._axis.conversion_factor = float(settings.value('conversion_factor', 1.0).toPyObject())
        self._axis.home_limit = float(settings.value('home_limit', 1).toPyObject())
        self.strokeSpinBox.setValue(float(settings.value('stroke', 1).toPyObject()))
        self.speedSpinBox.setValue(float(settings.value('speed', 1).toPyObject()))
        self.homingTorqueSpinBox.setValue(float(settings.value('homing_torque', 1).toPyObject()))
        self._axis.is_homed = bool(settings.value('is_homed', False).toPyObject())
        settings.endGroup()

    def writeSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup(self.name)
        settings.setValue('conversion_factor', self._axis.conversion_factor)
        settings.setValue('stroke', self.strokeSpinBox.value())
        settings.setValue('speed', self.speedSpinBox.value())
        settings.setValue('homing_torque', self.homingTorqueSpinBox.value())
        settings.setValue('home_limit', self._axis.home_limit)
        settings.setValue('is_homed', self._axis.is_homed)
        settings.endGroup()

    def toolBoxChanged(self, index):
        if self.toolBox.currentWidget() is self.configurationWidget:
            self.convFactorSpinBox.setValue(float(self._axis.conversion_factor))
            self.limitSpinBox.setValue(self._axis.home_limit)

    def showEvent(self, event):
        super(AxisTwoState, self).showEvent(event)
        self._autoRefresh.start(self._refresh_rate)

    def hideEvent(self, event):
        super(AxisTwoState, self).hideEvent(event)
        self._autoRefresh.stop()

    def refresh(self):
        '''Updates all views with data from controller.'''
        # information
        if self._axis.controller.connected is True:
            if self.toolBox.currentWidget() is self.informationWidget:
                self.positionEdit.setText(str(self._axis.position))
                self.velocityEdit.setText(str(self._axis.velocity))
                self.torqueEdit.setText(str(self._axis.torque))
                self.errorEdit.setText(str(self._axis.error))

    def home(self):
        '''Finds the edges of the axis, then sets the center.'''
        homing_torque = float(self.homingTorqueSpinBox.value())
        speed = 3

        self._axis.home(speed, homing_torque)

    def right(self):
        stroke = (self.strokeSpinBox.value() / 100)
        speed = self.speedSpinBox.value()

        self._axis.rangeMove(speed, 0.5 + (stroke / 2))

    def left(self):
        stroke = (self.strokeSpinBox.value() / 100)
        speed = self.speedSpinBox.value()

        self._axis.rangeMove(speed, 0.5 - (stroke / 2))

    def center(self):
        speed = self.speedSpinBox.value()

        self._axis.rangeMove(speed, 0.5)

    def go(self):
        reps = self.repsSpinBox.value()
        stroke = (self.strokeSpinBox.value() / 100)
        speed = self.speedSpinBox.value()

        self._axis.pingPong(speed, reps, 0.5 - (stroke / 2), 0.5 + (stroke / 2))
