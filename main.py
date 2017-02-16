#!/usr/bin/python2
from PyQt4 import QtGui, QtCore
from views import View, ProgramTab, ConnectionTab, AxisSimple, AxisTwoState
from modules import GalilController, GalilAxis
import logging as log
import sys


class QtSignals(QtCore.QObject):
    '''Object for emmiting signals from non-QObjects'''
    append_log = QtCore.pyqtSignal(str)


class QtLogger(log.Handler):
    def __init__(self):
        super(QtLogger, self).__init__()
        self.setFormatter(log.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        log.getLogger().addHandler(self)
        log.getLogger().setLevel(log.DEBUG)
        self.signals = QtSignals()

    def emit(self, record):
        msg = self.format(record)
        self.signals.append_log.emit(msg)


class MainWindow(View['MainWindow']):

    closing = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # maximize
        #self.showMaximized()

        # identify app for QSettings
        QtCore.QCoreApplication.setOrganizationName('HP')
        QtCore.QCoreApplication.setOrganizationDomain('hp.com')
        QtCore.QCoreApplication.setApplicationName('Trolley Tester')

        # initialize
        self.setupBackend()
        self.setupFrontend()

    def setupBackend(self):
        # Controllers
        self.controllers = {
            'Galil 0': GalilController(),
            'Galil 1': GalilController()
        }

        # Axes
        self.axes = {
            'Hopper (Back)': GalilAxis('A', self.controllers['Galil 0']),
            'Trough (Back)': GalilAxis('B', self.controllers['Galil 0']),
            'Lifter (Back)': GalilAxis('A', self.controllers['Galil 1']),
            'Vane (Back)': GalilAxis('C', self.controllers['Galil 0']),
            'Hopper (Front)': GalilAxis('E', self.controllers['Galil 0']),
            'Trough (Front)': GalilAxis('F', self.controllers['Galil 0']),
            'Lifter (Front)': GalilAxis('B', self.controllers['Galil 1']),
            'Vane (Front)': GalilAxis('G', self.controllers['Galil 0'])
        }

        # setup logging window
        QtLogger().signals.append_log.connect(self.logView.appendPlainText)

    def setupFrontend(self):
        # Connection Tab
        self.connectionTab = ConnectionTab(self.controllers, self)
        self.tabWidget.addTab(self.connectionTab, 'Connection')

        # Front Simple Axis
        layout = QtGui.QHBoxLayout()
        layout.addWidget(AxisSimple(self.axes['Hopper (Front)'], 'Hopper', self))
        layout.addWidget(AxisSimple(self.axes['Trough (Front)'], 'Trough', self))
        layout.addWidget(AxisSimple(self.axes['Lifter (Front)'], 'Lifter', self))
        tab = QtGui.QWidget()
        tab.setLayout(layout)
        self.tabWidget.addTab(tab, 'Front Motors')

        # Back Simple Axis
        layout = QtGui.QHBoxLayout()
        layout.addWidget(AxisSimple(self.axes['Hopper (Back)'], 'Hopper', self))
        layout.addWidget(AxisSimple(self.axes['Trough (Back)'], 'Trough', self))
        layout.addWidget(AxisSimple(self.axes['Lifter (Back)'], 'Lifter', self))
        tab = QtGui.QWidget()
        tab.setLayout(layout)
        self.tabWidget.addTab(tab, 'Back Motors')

        # Vane Axis
        layout = QtGui.QHBoxLayout()
        layout.addWidget(AxisTwoState(self.axes['Vane (Front)'], 'Vane (Front)', self))
        layout.addWidget(AxisTwoState(self.axes['Vane (Back)'], 'Vane (Back)', self))
        tab = QtGui.QWidget()
        tab.setLayout(layout)
        self.tabWidget.addTab(tab, 'Vanes')

        # Program Tab
        self.programTab = ProgramTab(self.axes, self)
        self.tabWidget.addTab(self.programTab, 'Program')

    def closeEvent(self, event):
        self.closing.emit()
        event.accept()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
