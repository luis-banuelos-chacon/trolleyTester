from PyQt4 import QtCore
from . import View


class AxisManualControl(View['AxisManualControl']):

    _refresh_rate = 100

    def __init__(self, axis, parent=None):
        super(AxisManualControl, self).__init__(parent)
        self.setupUi(self)

        # controller
        self._axis = axis

        # settings
        self.readSettings()

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
        self.convFactorSpinBox.valueChanged.connect(lambda v: self._axis.__setattr__('conversion_factor', v))

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

        # connect window closing event
        if parent:
            parent.closing.connect(self.writeSettings)

    def readSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup(self._axis.name)
        self._axis.conversion_factor = settings.value('conversion_factor', 1.0).toPyObject()
        settings.endGroup()

    def writeSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup(self._axis.name)
        settings.setValue('conversion_factor', self._axis.conversion_factor)
        settings.endGroup()

    def toolBoxChanged(self, index):
        if self.toolBox.currentWidget() is self.configurationWidget:
            self.accelerationSpinBox.setValue(int(self._axis.acceleration))
            self.decelerationSpinBox.setValue(int(self._axis.deceleration))
            self.torqueLimitSpinBox.setValue(float(self._axis.torque_limit))
            self.convFactorSpinBox.setValue(float(self._axis.conversion_factor))

    def showEvent(self, event):
        super(AxisManualControl, self).showEvent(event)
        self._autoRefresh.start(self._refresh_rate)

    def hideEvent(self, event):
        super(AxisManualControl, self).hideEvent(event)
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
        try:
            self._axis.wait()
        except:
            pass
        self._axis.disable()

    def setJogSpeed(self, speed):
        '''Sets new jog speed on the fly.'''
        if self._axis.jog >= 0:
            self._axis.jog = speed
        else:
            self._axis.jog = (speed * -1)
