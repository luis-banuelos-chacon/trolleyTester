from PyQt4 import QtCore
import time


class ProgramThread(QtCore.QThread):

    instruction_changed = QtCore.pyqtSignal(int)

    def __init__(self, axes, program, loops, parent=None):
        super(ProgramThread, self).__init__(parent)

        # sorted has the side effect of creating a new list
        self.program = sorted(program, key=lambda k: k['time'])
        self.loops = loops
        self.axes = axes

        # flags
        self.elapsed = 0        # elapsed time
        self.running = False    # program running
        self.loop = 0           # current loop iteration
        self.pc = 0             # program counter

    def execute(self, axis, action, args):
        axis = self.axes[axis]

        if action == 'Timed':
            axis.timedMove(*args)

        if action == 'Range':
            axis.rangeMove(*args)

        if action == 'PingPong':
            speed = args[0]
            stroke = args[1]
            repeats = args[2]

            a = 0.5 - (stroke / 200.0)
            b = 0.5 + (stroke / 200.0)

            axis.pingPong(speed, repeats, a, b)

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        self.loop = 0
        self.pc = 0

        start = time.time() * 1000.0
        while self.running:
            self.elapsed = (time.time() * 1000.0) - start
            task = self.program[self.pc]

            if self.elapsed > task['time']:
                self.execute(task['axis'], task['action'], task['args'])
                self.pc += 1
                self.instruction_changed.emit(self.pc)

            if self.pc == len(self.program):
                # wait until all axes finish execution:
                for axis in self.axes.values():
                    while axis.running:
                        pass

                start = time.time() * 1000.0
                self.loop += 1
                self.pc = 0

            if not self.loops == 0 and self.loop == self.loops:
                break

            time.sleep(0.001)

        # stop all axis
        for axis in self.axes.values():
            axis.cancel()











