import logging as log
import gclib


class GalilController(object):

    def __init__(self, address=None, baud=None):
        '''Initializes a Galil Controller.'''
        self._g = gclib.py()            # instance of gclib class

        self.connected = False          # connection flag

        if address is not None:
            self.open(address, baud)    # open connection
            self.disable()              # turn off motors

    ##
    # Basic Wrappers
    ##

    def open(self, address, baud=None):
        '''Opens connection to controller.'''
        cmd_string = '-a ' + str(address)
        if baud is not None:
            cmd_string = cmd_string + ' -b ' + str(baud)

        cmd_string = cmd_string + ' --direct'

        try:
            self._g.GOpen(cmd_string)
            self.connected = True
            log.info('Connected to controller at (' + str(address) + ')')
            return True

        except gclib.GclibError:
            log.error('No response from controller at (' + str(address) + ')')
            return False

    def close(self):
        '''Closes active connection to controller.'''
        log.info('Disconnected from controller.')
        self._g.GClose()
        self.connected = False

    def info(self):
        '''Returns info string from controller.'''
        try:
            return self._g.GInfo()

        except gclib.GclibError:
            log.error('No active connection.')

    def command(self, command):
        '''Wrapper for GCommand.'''
        return self._g.GCommand(command)

    ##
    # System
    ##

    def burnParameters(self):
        self.command('BN')

    def burnProgram(self):
        self.command('BP')

    ##
    # Motion
    ##

    def enable(self):
        '''Enables servos.'''
        self.command('SH')

    def disable(self):
        '''Disables servo.'''
        self.command('MO')

    def begin(self):
        '''Begins motion on all axes.'''
        self.command('BG')

    def stop(self):
        '''Stops motion before end of move on all axes.'''
        self.command('ST')

    ##
    # IO
    ##

    def getInput(self, _in):
        return float(self.command('MG@IN[' + str(_in) + ']'))

    def getOutput(self, _out):
        return float(self.command('MG@OUT[' + str(_out) + ']'))

    def setOutput(self, output, value):
        if value in [True, 1]:
            self.command('SB' + str(output))
        else:
            self.command('CB' + str(output))


class GalilAxis(GalilController):

    def __init__(self, axis, parent=None):
        '''Binds to a gclib instance from a GalilWrapper.'''
        self._parent = parent
        self._g = parent._g
        self._axis = axis.upper()

    ##
    # Methods
    ##

    def getData(self, command):
        '''Returns data from command on current axis.'''
        cmd_string = command.upper() + self._axis.upper() + '=?'
        data = self.command(cmd_string)
        return float(data)

    def setData(self, command, value):
        '''Sets data at command on current axis.'''
        cmd_string = command.upper() + self._axis.upper() + '=' + str(value)
        try:
            self.command(cmd_string)
        except gclib.GclibError:
            return False
        return True

    ##
    # Motion
    ##

    def enable(self):
        '''Enables servos.'''
        self.command('SH' + self._axis)

    def disable(self):
        '''Disables servo.'''
        self.command('MO' + self._axis)

    def begin(self):
        '''Begins motion on all axes.'''
        self.command('BG' + self._axis)

    def stop(self):
        '''Stops motion before end of move on all axes.'''
        self.command('ST' + self._axis)

    def wait(self):
        '''Blocks until the motion completes.'''
        self._g.GMotionComplete(self._axis)

    ##
    # Properties
    ##

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, value):
        self._axis = str(value).upper()

    # Independent Axis Positioning

    @property
    def position_relative(self):
        return self.getData('PR')

    @position_relative.setter
    def position_relative(self, value):
        self.setData('PR', value)

    @property
    def position_absolute(self):
        return self.getData('PA')

    @position_absolute.setter
    def position_absolute(self, value):
        self.setData('PA', value)

    @property
    def speed(self):
        return self.getData('SP')

    @speed.setter
    def speed(self, value):
        self.setData('SP', value)

    @property
    def acceleration(self):
        return self.getData('AC')

    @acceleration.setter
    def acceleration(self, value):
        self.setData('AC', value)

    @property
    def deceleration(self):
        return self.getData('DC')

    @deceleration.setter
    def deceleration(self, value):
        self.setData('DC', value)

    @property
    def increment_position(self):
        return self.getData('IP')

    @increment_position.setter
    def increment_position(self, value):
        self.setData('IP', value)

    @property
    def time_constant(self):
        return self.getData('IT')

    @time_constant.setter
    def time_constant(self, value):
        self.setData('IT', value)

    @property
    def profiler_complete(self):
        return self.getData('AM')

    @profiler_complete.setter
    def profiler_complete(self, value):
        self.setData('AM', value)

    @property
    def in_position(self):
        return self.getData('MC')

    @in_position.setter
    def in_position(self, value):
        self.setData('MC', value)

    # Independent Jogging

    @property
    def jog(self):
        return self.getData('JG')

    @jog.setter
    def jog(self, value):
        self.setData('JG', value)

    # Filter / Control

    @property
    def kp(self):
        return self.getData('KP')

    @kp.setter
    def kp(self, value):
        self.setData('KP', value)

    @property
    def ki(self):
        return self.getData('KI')

    @ki.setter
    def ki(self, value):
        self.setData('KI', value)

    @property
    def kd(self):
        return self.getData('KD')

    @kd.setter
    def kd(self, value):
        self.setData('KD', value)

    @property
    def offset(self):
        return self.getData('OF')

    @offset.setter
    def offset(self, value):
        self.setData('OF', value)

    @property
    def integrator_limit(self):
        return self.getData('IL')

    @integrator_limit.setter
    def integrator_limit(self, value):
        self.setData('IL', value)

    @property
    def torque_limit(self):
        return self.getData('TL')

    @torque_limit.setter
    def torque_limit(self, value):
        self.setData('TL', value)

    # Interrogation

    @property
    def position(self):
        return float(self.command('TP' + self._axis))

    @property
    def torque(self):
        return float(self.command('TT' + self._axis))

    @property
    def velocity(self):
        return float(self.command('TV' + self._axis))

    @property
    def error(self):
        return float(self.command('TE' + self._axis))
