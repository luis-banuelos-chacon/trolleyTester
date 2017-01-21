from threading import Thread, Timer, Lock, Event
import logging as log
import gclib
import time


class GalilController(object):

    def __init__(self, name=None, address=None, baud=None):
        '''Initializes a Galil Controller.'''
        self._g = gclib.py()            # instance of gclib class
        self._g.lock = Lock()           # insert a lock for thread safe interactions

        self.name = name                # coontroller name
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
            log.info('[{}] Connected at ({})'.format(self.name, address))
            return True

        except gclib.GclibError:
            log.error('[{}] No response at ({})'.format(self.name, address))
            return False

    def close(self):
        '''Closes active connection to controller.'''
        log.info('[{}] Disconnected.'.format(self.name))
        self._g.GClose()
        self.connected = False

    def info(self):
        '''Returns info string from controller.'''
        try:
            return self._g.GInfo()

        except gclib.GclibError:
            log.error('[{}] No active connection.'.format(self.name))

    def command(self, command):
        '''Wrapper for GCommand.'''
        with self._g.lock:
            try:
                ret = self._g.GCommand(command)
            except gclib.GclibError:
                ret = '-1'
            log.debug('{} -> {}'.format(command, ret))
            return ret

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


class GalilAbstractAxis(GalilController):

    def __init__(self, axis, parent=None, name=None):
        '''Binds to a gclib instance from a GalilWrapper.'''
        if name is not None:
            self.name = name
        else:
            self.name = str(axis)

        self.controller = parent
        self._parent = parent
        self._g = parent._g
        self._axis = axis.upper()

        # vars
        self._conversion_factor = 1.0

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

    def home(self):
        '''Sets current position to 0.'''
        self.setData('DP', 0)

    def enable(self):
        '''Enables servos.'''
        self.command('SH' + self._axis)

    def disable(self):
        '''Disables servo.'''
        self.command('MO' + self._axis)

    def begin(self):
        '''Begins motion.'''
        self.command('BG' + self._axis)

    def stop(self):
        '''Stops motion before end of move.'''
        self.command('ST' + self._axis)

    def wait(self):
        '''Blocks until the motion completes.'''
        try:
            with self._g.lock:
                self._g.GMotionComplete(self._axis)
        except:
            pass

    ##
    # Properties
    ##

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, value):
        self._axis = str(value).upper()

    # configuration

    @property
    def brush_mode(self):
        return self.getData('BR')

    @brush_mode.setter
    def brush_mode(self, value):
        self.setData('BR', value)

    @property
    def conversion_factor(self):
        try:
            return self._conversion_factor
        except:
            self._conversion_factor = 1
            return self._conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value):
        self._conversion_factor = float(value)

    # Independent Axis Positioning

    @property
    def position_relative(self):
        return self.getData('PR') / self._conversion_factor

    @position_relative.setter
    def position_relative(self, value):
        self.setData('PR', value * self._conversion_factor)

    @property
    def position_absolute(self):
        return self.getData('PA') / self._conversion_factor

    @position_absolute.setter
    def position_absolute(self, value):
        self.setData('PA', value * self._conversion_factor)

    @property
    def speed(self):
        return self.getData('SP') / self._conversion_factor

    @speed.setter
    def speed(self, value):
        self.setData('SP', value * self._conversion_factor)

    @property
    def acceleration(self):
        return self.getData('AC') / self._conversion_factor

    @acceleration.setter
    def acceleration(self, value):
        self.setData('AC', value * self._conversion_factor)

    @property
    def deceleration(self):
        return self.getData('DC') / self._conversion_factor

    @deceleration.setter
    def deceleration(self, value):
        self.setData('DC', value * self._conversion_factor)

    @property
    def increment_position(self):
        return self.getData('IP') / self._conversion_factor

    @increment_position.setter
    def increment_position(self, value):
        self.setData('IP', value * self._conversion_factor)

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
        return self.getData('MC') / self._conversion_factor

    @in_position.setter
    def in_position(self, value):
        self.setData('MC', value * self._conversion_factor)

    # Independent Jogging

    @property
    def jog(self):
        return self.getData('JG') / self._conversion_factor

    @jog.setter
    def jog(self, value):
        self.setData('JG', value * self._conversion_factor)

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
        return float(self.command('TP' + self._axis)) / self._conversion_factor

    @property
    def torque(self):
        return float(self.command('TT' + self._axis))

    @property
    def velocity(self):
        return float(self.command('TV' + self._axis)) / self._conversion_factor

    @property
    def error(self):
        return float(self.command('TE' + self._axis)) / self._conversion_factor


class GalilAxis(GalilAbstractAxis):

    def __init__(self, *args, **kwargs):
        super(GalilAxis, self).__init__(*args, **kwargs)

        self.homed = False
        self.limit = 0.0

        # list of scheduled tasks
        # items are tuples (func, (args))
        self.tasks = []

        # execute scheduler
        sched = Thread(target=self.loop, args=())
        sched.daemon = True
        sched.start()

    ##
    # Scheduler
    ##

    def cancel(self):
        '''Clears task list and disables axis.'''
        self.tasks = [
            (self.stop,),
            (self.wait,),
            (self.disable,)
        ]

    def loop(self):
        '''Iterates through task list indefinitely.'''
        while True:
            if len(self.tasks) > 0:
                task = self.tasks.pop(0)

                if len(task) == 1:
                    # execute task with no arguments
                    task[0]()

                elif isinstance(task[0], str):
                    # set variable
                    if isinstance(task[1], str):
                        value = self.__getattribute__(task[1])
                    else:
                        value = task[1]

                    self.__setattr__(task[0], value)

                else:
                    # execute task with arguments
                    task[0](*task[1:])

                time.sleep(0.01)

    ##
    # Methods
    ##

    def jogMove(self, speed):
        '''Moves axis at speed indefinitely.'''
        task = [
            ('jog', speed),
            (self.enable,),
            (self.begin,)
        ]
        self.tasks.extend(task)

    def relativeMove(self, speed, pos):
        '''Moves to a relative position.'''
        task = [
            ('position_relative', pos),
            ('speed', speed),
            (self.enable,),
            (self.begin,)
        ]
        self.tasks.extend(task)

    def timedMove(self, speed, t):
        '''Moves axis at speed for time.'''
        self.relativeMove(speed, speed * t)

    def home(self, speed, torque):
        '''Finds left and right limits.'''
        def blockUntilTorque(torque):
            while (abs(self.torque) < torque):
                time.sleep(0.1)

        task = [
            # find left edge
            ('jog', -speed),
            (self.enable,),
            (self.begin,),
            (blockUntilTorque, torque),
            (self.stop,),
            (self.wait,),
            (super(GalilAxis, self).home,),

            # find right edge
            ('jog', speed),
            (self.begin,),
            (blockUntilTorque, torque),
            (self.stop,),
            (self.wait,),
            (self.disable,),
            ('limit', 'position'),
            ('homed', True)
        ]
        self.tasks.extend(task)

    def absoluteMove(self, speed, pos):
        '''Moves to an absolute position from home.'''
        if self.homed:
            task = [
                ('position_absolute', pos),
                ('speed', speed),
                (self.enable,),
                (self.begin,)
            ]
            self.tasks.extend(task)

    def rangeMove(self, speed, pos):
        '''Moves within ranges found by homing.'''
        if self.homed:
            task = [
                ('position_absolute', self.limit * pos),
                ('speed', speed),
                (self.enable,),
                (self.begin,)
            ]
            self.tasks.extend(task)

    def pingPong(self, speed, repeats, a, b):
        '''Bounces between positions.'''
        task = [(self.enable,), ('speed', speed)]
        for i in range(repeats):
            task.append(('position_absolute', self.limit * a))
            task.append((self.begin,))
            task.append((self.wait,))
            task.append(('position_absolute', self.limit * b))
            task.append((self.begin,))
            task.append((self.wait,))

        task.append((self.stop,))
        task.append((self.wait,))
        task.append((self.disable,))
        self.tasks.extend(task)
