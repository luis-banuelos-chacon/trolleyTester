from PyQt4 import QtCore
import time


class ProgramThread(QtCore.QThread):

    instruction_changed = QtCore.pyqtSignal(int)

    def __init__(self, program, parent=None):
        super(ProgramThread, self).__init__(parent)

        # make an actual copy that we can modify
        self._program = list(program)

        # get all axes
        self._axes = list(set([item['axis'] for item in self._program]))

        # stop flag
        self._stop = False

        # loop flag (public)
        self.loop = False

    def stop(self):
        self.stopAxis()
        self._stop = True

    def stopAxis(self, axis=None):
        if axis:
            axis.stop()
            axis.wait()
            axis.disable()
        else:
            for axis in self._axes:
                axis.stop()
                axis.wait()
                axis.disable()

    def jogAxis(self, axis, speed):
        axis.jog = speed
        axis.enable()
        axis.begin()

    def timedAxis(self, axis, speed):
        axis.jog = speed
        axis.enable()
        axis.begin()

    def parse(self, program):
        # parsed event list
        # list of (index, time, method, args)
        events = []

        for idx, item in enumerate(program):
            start = item['time']
            axis = item['axis']
            speed = item['speed']
            duration = item['duration']
            action = item['action']

            if action == 'timed move':
                events.append((idx, start, self.jogAxis, [axis, speed]))
                events.append((idx, start+duration, self.stopAxis, [axis]))
                continue

            if action == 'jog move':
                events.append((idx, start, self.jogAxis, [axis, speed]))
                continue

            if action == 'stop':
                events.append((idx, start, self.stopAxis, [axis]))
                continue

        events = sorted(events, key=lambda l: l[1])
        return events

    def run(self):
        # initial time
        initial_time = time.time()*1000.0

        # parse program
        events = self.parse(self._program)

        # current event
        current = 0

        while True:
            index = events[current][0]
            start_time = events[current][1]
            method = events[current][2]
            args = events[current][3]

            while True:
                elapsed_time = (time.time()*1000.0) - initial_time

                if elapsed_time > start_time:
                    method(*args)
                    self.instruction_changed.emit(index)
                    break

                if self._stop:
                    break

                time.sleep(0.001)

            if self._stop:
                break

            if current < len(events) - 1:
                current += 1
            elif self.loop is True:
                initial_time = time.time()*1000.0
                current = 0
            else:
                break
