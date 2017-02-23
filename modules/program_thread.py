from PyQt4 import QtCore
import time


class ProgramThread(QtCore.QThread):

    instruction_changed = QtCore.pyqtSignal(int)
    iteration_changed = QtCore.pyqtSignal(int)

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
            speed = args[0]
            duration = args[1] / 1000.0

            axis.timedMove(speed, duration)

        if action == 'Range':
            speed = args[0]
            position = args[1] / 100.0

            axis.rangeMove(speed, position)

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
                self.instruction_changed.emit(self.pc)
                self.pc += 1

            if self.pc == len(self.program):
                # wait until all axes finish execution:
                for axis in self.axes.values():
                    while axis.running and self.running:
                        time.sleep(0.01)
                        pass

                start = time.time() * 1000.0
                self.loop += 1
                self.pc = 0
                self.iteration_changed.emit(self.loop)

            if not self.loops == 0 and self.loop == self.loops:
                break

            time.sleep(0.01)

        # stop all axis
        for axis in self.axes.values():
            axis.cancel()











