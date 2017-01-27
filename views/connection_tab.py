from PyQt4 import QtCore
from . import View


class ConnectionTab(View['ConnectionTab']):

    def __init__(self, controllers, parent=None):
        super(ConnectionTab, self).__init__(parent)
        self.setupUi(self)

        # get reference to controllers
        self.controllers = controllers

        # widgets into lists
        self.ip = []
        self.ip.append((self.ip0_0, self.ip1_0, self.ip2_0, self.ip3_0))
        self.ip.append((self.ip0_1, self.ip1_1, self.ip2_1, self.ip3_1))
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
        for i in range(4):
            self.ip[0][i].setValue(int(settings.value('ip_0', '0.0.0.0').toPyObject().split('.')[i]))
            self.ip[1][i].setValue(int(settings.value('ip_1', '0.0.0.0').toPyObject().split('.')[i]))
        settings.endGroup()

    def writeSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup('ConnectionTab')
        settings.setValue('ip_0', self.getIP(self.ip[0]))
        settings.setValue('ip_1', self.getIP(self.ip[1]))
        settings.endGroup()

    def getIP(self, ip):
        return '{}.{}.{}.{}'.format(ip[0].value(), ip[1].value(), ip[2].value(), ip[3].value())

    def connect(self, id):
        name = ['Galil 0', 'Galil 1'][id]

        if self.controllers[name].connected:
            # disconnect
            self.controllers[name].close()
            self.connect_btn[id].setText('Connect')

        else:
            # connect
            self.connect_btn[id].setDown(True)

            if self.controllers[name].open(self.getIP(self.ip[id])):
                self.controllers[name].disable()
                self.connect_btn[id].setText('Disconnect')
            else:
                self.connect_btn[id].setText('Connect')

            self.connect_btn[id].setDown(False)
