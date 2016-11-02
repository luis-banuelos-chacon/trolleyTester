from PyQt4 import QtCore
from . import View


class ConnectionTab(View['ConnectionTab']):

    def __init__(self, galil, parent=None):
        super(ConnectionTab, self).__init__(parent)
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
        self.connect_btn[0].clicked.connect(lambda v, i=0: self.connect(i))
        self.connect_btn[1].clicked.connect(lambda v, i=1: self.connect(i))

        # settings
        self.readSettings()

        # connect window closing event
        if parent:
            parent.closing.connect(self.writeSettings)

    def readSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup('ConnectionTab')
        self.address[0].setText(settings.value('address_0', '').toPyObject())
        self.address[1].setText(settings.value('address_1', '').toPyObject())
        settings.endGroup()

    def writeSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup('ConnectionTab')
        settings.setValue('address_0', self.address[0].text())
        settings.setValue('address_1', self.address[1].text())
        settings.endGroup()

    def connect(self, id):
        if self.galil[id].connected:
            # disconnect
            self.galil[id].close()
            self.connect_btn[id].setText('Connect')

        else:
            # connect
            self.connect_btn[id].setDown(True)

            if self.galil[id].open(str(self.address[id].text())):
                self.galil[id].disable()
                self.connect_btn[id].setText('Disconnect')
            else:
                self.connect_btn[id].setText('Connect')

            self.connect_btn[id].setDown(False)
