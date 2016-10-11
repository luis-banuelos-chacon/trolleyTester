from PyQt4 import QtGui, QtCore
from views import ViewBase, ViewForm
from modules import GalilController, GalilAxis
import logging as log
import sys


class QLogger(log.Handler):
    def __init__(self, widget):
        super(QLogger, self).__init__()

        self.widget = widget
        self.widget.setReadOnly(True)

        self.setFormatter(log.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        log.getLogger().addHandler(self)
        log.getLogger().setLevel(log.DEBUG)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class ConnectionTab(ViewBase['ConnectionTab'], ViewForm['ConnectionTab']):

    def __init__(self, galil, parent=None):
        super(ViewBase['ConnectionTab'], self).__init__(parent)
        self.setupUi(self)

        # get reference to galil controllers
        self.galil = galil

        # widgets into lists
        self.address = []
        self.address.append(self.address_0)
        self.address.append(self.address_1)
        self.connect_btn = []
        self.connect_btn.append(self.connect_0)
        self.connect_btn.append(self.connect_1)

        # connect signals
        self.connect_btn[0].clicked.connect(lambda i=0: self.connect(i))
        self.connect_btn[1].clicked.connect(lambda i=1: self.connect(i))

    def connect(self, id):
        if self.galil[id].connected:
            # disconnect
            self.galil[id].close()
            self.connect_btn[id].setText('Connect')

        else:
            # connect
            self.connect_btn[id].setDown(True)

            if self.galil[id].open(str(self.address[id].text())):
                self.connect_btn[id].setText('Disconnect')
            else:
                self.connect_btn[id].setText('Connect')

            self.connect_btn[id].setDown(False)


class MainWindow(ViewBase['MainWindow'], ViewForm['MainWindow']):

    def __init__(self, parent=None):
        super(ViewBase['MainWindow'], self).__init__(parent)
        self.setupUi(self)

        self.setupBackend()
        self.setupFrontend()

    def setupBackend(self):
        # Galil Controllers
        self.galil = []
        self.galil.append(GalilController('Galil 0 - 24V'))
        self.galil.append(GalilController('Galil 1 - 48V'))

        # setup logging window
        QLogger(self.logView)

    def setupFrontend(self):
        # Connection Tab
        self.connectionTab = ConnectionTab(self.galil, self)
        self.tabWidget.addTab(self.connectionTab, 'Connection')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
