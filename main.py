from PyQt4 import QtGui, QtCore
from views import View, ProgramTab, ConnectionTab, AxisManualControl
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

        # self.axis = GalilAxis('X', self.galil[0])

        # Axis
        self.axes = []
        self.axes.append(GalilAxis('A', self.galil[0], 'Hopper (Back)'))
        self.axes.append(GalilAxis('B', self.galil[0], 'Trough (Back)'))
        self.axes.append(GalilAxis('A', self.galil[1], 'Lifter (Back)'))
        self.axes.append(GalilAxis('E', self.galil[0], 'Hopper (Front)'))
        self.axes.append(GalilAxis('F', self.galil[0], 'Trough (Front)'))
        self.axes.append(GalilAxis('B', self.galil[1], 'Lifter (Front)'))

        # setup logging window
        QtLogger().signals.append_log.connect(self.logView.appendPlainText)

    def setupFrontend(self):
        # Connection Tab
        self.connectionTab = ConnectionTab(self.galil, self)
        self.tabWidget.addTab(self.connectionTab, 'Connection')

        # Autofill Axis
        layout = QtGui.QHBoxLayout()
        for i, axis in enumerate(self.axes):
            layout.addWidget(AxisManualControl(axis, self))

            if i % 3 >= 2 or i == len(self.axes) - 1:
                tab = QtGui.QWidget()
                tab.setLayout(layout)
                self.tabWidget.addTab(tab, 'Page ' + str(i / 3))
                layout = QtGui.QHBoxLayout()

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
