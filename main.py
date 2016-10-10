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


class MainWindow(ViewBase['MainWindow'], ViewForm['MainWindow']):

    def __init__(self, parent=None):
        super(ViewBase['MainWindow'], self).__init__(parent)
        self.setupUi(self)

        self.setupBackend()
        self.setupFrontend()

    def setupBackend(self):
        # Galil Controllers
        self.galilA = GalilController()
        self.galilB = GalilController()

        # setup logging window
        QLogger(self.logView)

    def setupFrontend(self):
        # Connect buttons
        self.galilAConnectButton.clicked.connect(self.galilAConnect)
        self.galilBConnectButton.clicked.connect(self.galilBConnect)

    def galilAConnect(self):
        if self.galilA.connected is not True:
            # get address
            address = str(self.galilAAddress.text())

            # blank button
            self.galilAConnectButton.setDown(True)
            self.galilAConnectButton.setText('Connecting...')

            # try to open connection
            ret = self.galilA.open(address)

            if ret is True:
                self.galilAConnectButton.setDown(False)
                self.galilAConnectButton.setText('Disconnect')
            else:
                self.galilAConnectButton.setDown(False)
                self.galilAConnectButton.setText('Connect')
        else:
            self.galilA.close()
            self.galilAConnectButton.setText('Connect')

    def galilBConnect(self):
        if self.galilB.connected is not True:
            # get address
            address = str(self.galilBAddress.text())

            # blank button
            self.galilBConnectButton.setDown(True)
            self.galilBConnectButton.setText('Connecting...')

            # try to open connection
            ret = self.galilB.open(address)

            if ret is True:
                self.galilBConnectButton.setDown(False)
                self.galilBConnectButton.setText('Disconnect')
            else:
                self.galilBConnectButton.setDown(False)
                self.galilBConnectButton.setText('Connect')
        else:
            self.galilB.close()
            self.galilBConnectButton.setText('Connect')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
