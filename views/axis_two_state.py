from PyQt4 import QtCore
from threading import Thread
from . import View
import time


class AxisTwoState(View['AxisTwoState']):

    _refresh_rate = 100

    def __init__(self, axis, parent=None):
        super(AxisTwoState, self).__init__(parent)
        self.setupUi(self)

        # controller
        self._axis = axis

        # settings
        self.readSettings()

        # set name
        self.mainBox.setTitle(self._axis.name)

        # motion
        self.goButton.clicked.connect(self.go)
        self.centerButton.clicked.connect(self.center)
        self.rightButton.clicked.connect(self.right)
        self.leftButton.clicked.connect(self.left)

        # configuration
        self.homeButton.clicked.connect(self.home)
        self.convFactorSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('conversion_factor', v))

        # stop
        self.stopButton.clicked.connect(self.stop)

        # data polling
        self._autoRefresh = QtCore.QTimer(self)
        self._autoRefresh.timeout.connect(self.refresh)

        # tool box changed
        self.toolBox.currentChanged.connect(self.toolBoxChanged)

        # connect window closing event
        if parent:
            parent.closing.connect(self.writeSettings)

        # thread killer
        self._stop = False

    def readSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup(self._axis.name)
        self._axis.conversion_factor = settings.value('conversion_factor', 1.0).toPyObject()
        self.strokeSpinBox.setValue(settings.value('stroke', 1).toPyObject())
        self.speedSpinBox.setValue(settings.value('speed', 1).toPyObject())
        self.homingTorqueSpinBox.setValue(settings.value('homing_torque', 1).toPyObject())
        self.limitSpinBox.setValue(settings.value('limit', 1).toPyObject())
        settings.endGroup()

    def writeSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup(self._axis.name)
        settings.setValue('conversion_factor', self._axis.conversion_factor)
        settings.setValue('stroke', self.strokeSpinBox.value())
        settings.setValue('speed', self.speedSpinBox.value())
        settings.setValue('homing_torque', self.homingTorqueSpinBox.value())
        settings.setValue('limit', self.limitSpinBox.value())
        settings.endGroup()

    def toolBoxChanged(self, index):
        if self.toolBox.currentWidget() is self.configurationWidget:
            self.convFactorSpinBox.setValue(float(self._axis.conversion_factor))

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

    def stop(self):
        '''Stops the current move.'''
        self._stop = True
        self._axis.stop()
        try:
            self._axis.wait()
        except:
            pass
        self._axis.disable()

    def home(self):
        '''Finds the edges of the axis, then sets the center.'''
        homing_torque = float(self.homingTorqueSpinBox.value())
        speed = 3

        def task():
            self._axis.enable()

            # find home
            self._axis.jog = -speed
            self._axis.begin()
            while (abs(self._axis.torque) < homing_torque):
                time.sleep(0.05)
                if self._stop:
                    self._stop = False
                    return

            self._axis.stop()
            self._axis.wait()
            self._axis.home()

            # find limit
            self._axis.jog = speed
            self._axis.begin()
            while (abs(self._axis.torque) < homing_torque):
                time.sleep(0.05)
                if self._stop:
                    self._stop = False
                    return

            self._axis.stop()
            self._axis.wait()
            self.limitSpinBox.setValue(self._axis.position)
            self._axis.disable()

        Thread(target=task, args=()).start()

    def right(self):
        limit = self.limitSpinBox.value()
        stroke = self.strokeSpinBox.value()
        speed = self.speedSpinBox.value()
        self._axis.position_absolute = (limit / 2) + stroke
        self._axis.speed = speed
        self._axis.enable()
        self._axis.begin()

    def left(self):
        limit = self.limitSpinBox.value()
        stroke = self.strokeSpinBox.value()
        speed = self.speedSpinBox.value()
        self._axis.position_absolute = (limit / 2) - stroke
        self._axis.speed = speed
        self._axis.enable()
        self._axis.begin()

    def center(self):
        limit = self.limitSpinBox.value()
        speed = self.speedSpinBox.value()
        self._axis.position_absolute = (limit / 2)
        self._axis.speed = speed
        self._axis.enable()
        self._axis.begin()

    def go(self):
        limit = self.limitSpinBox.value()
        stroke = self.strokeSpinBox.value()
        speed = self.speedSpinBox.value()

        def task():
            self._axis.enable()
            self._axis.speed = speed

            while (True):
                self._axis.position_absolute = (limit / 2) + stroke
                self._axis.begin()
                self._axis.wait()

                if self._stop:
                    self._stop = False
                    return

                self._axis.position_absolute = (limit / 2) - stroke
                self._axis.begin()
                self._axis.wait()

                if self._stop:
                    self._stop = False
                    return

        Thread(target=task, args=()).start()

