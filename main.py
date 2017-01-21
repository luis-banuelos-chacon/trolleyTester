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
        # Galil Controllers
        self.galil = []
        self.galil.append(GalilController('Galil 0 - 24V'))
        self.galil.append(GalilController('Galil 1 - 48V'))

        # Axis
        self.axes = {
            'Back': {
                'Hopper': GalilAxis('A', self.galil[0], 'Hopper (Back)'),
                'Trough': GalilAxis('B', self.galil[0], 'Trough (Back)'),
                'Lifter': GalilAxis('A', self.galil[1], 'Lifter (Back)'),
                'Vane': GalilAxis('C', self.galil[0], 'Vane (Back)')
            },
            'Front': {
                'Hopper': GalilAxis('E', self.galil[0], 'Hopper (Front)'),
                'Trough': GalilAxis('F', self.galil[0], 'Trough (Front)'),
                'Lifter': GalilAxis('B', self.galil[1], 'Lifter (Front)'),
                'Vane': GalilAxis('D', self.galil[0], 'Vane (Front)')
            }
        }

        # self.axis = GalilAxis('A', self.galil[0], 'Test')

        # setup logging window
        QtLogger().signals.append_log.connect(self.logView.appendPlainText)

    def setupFrontend(self):
        # Connection Tab
        self.connectionTab = ConnectionTab(self.galil, self)
        self.tabWidget.addTab(self.connectionTab, 'Connection')

        # widget = AxisTwoState(self.axis)
        # self.tabWidget.addTab(widget, 'TwoState')

        # widget = AxisSimple(self.axis)
        # self.tabWidget.addTab(widget, 'Simple')

        # Front Simple Axis
        layout = QtGui.QHBoxLayout()
        layout.addWidget(AxisSimple(self.axes['Front']['Hopper']))
        layout.addWidget(AxisSimple(self.axes['Front']['Trough']))
        layout.addWidget(AxisSimple(self.axes['Front']['Lifter']))
        tab = QtGui.QWidget()
        tab.setLayout(layout)
        self.tabWidget.addTab(tab, 'Front Motors')

        # Back Simple Axis
        layout = QtGui.QHBoxLayout()
        layout.addWidget(AxisSimple(self.axes['Back']['Hopper']))
        layout.addWidget(AxisSimple(self.axes['Back']['Trough']))
        layout.addWidget(AxisSimple(self.axes['Back']['Lifter']))
        tab = QtGui.QWidget()
        tab.setLayout(layout)
        self.tabWidget.addTab(tab, 'Back Motors')

        # Vane Axis
        layout = QtGui.QHBoxLayout()
        layout.addWidget(AxisTwoState(self.axes['Front']['Vane']))
        layout.addWidget(AxisTwoState(self.axes['Back']['Vane']))
        tab = QtGui.QWidget()
        tab.setLayout(layout)
        self.tabWidget.addTab(tab, 'Vanes')

        # Program Tab
        # self.programTab = ProgramTab(self.axes, self)
        # self.tabWidget.addTab(self.programTab, 'Program')

    def closeEvent(self, event):
        self.closing.emit()
        event.accept()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
