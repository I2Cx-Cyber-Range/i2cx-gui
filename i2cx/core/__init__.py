from PySide6 import QtGui
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Signal, Slot,QUrl,QSize
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtCore import Qt 

import os

class Core:
    BASE_URL = "ftdi://ftdi:i2cx-scanner-lite/"
    
    def __init__(self,app):
        self.app = app
        self.pluginName = "Core"
        self.ui = self.loadUI()
        self.connectEvents()
     
    def loadUI(self):
        loader = QUiLoader()
        file = QFile(os.path.join(os.path.dirname(__file__), "gui/gui.ui"))
        file.open(QFile.ReadOnly)
        ui = loader.load(file)

        ui.icon = QIcon(os.path.join(os.path.dirname(__file__), "assets/logo_cyber_range.png"))

        rotate90 = QtGui.QTransform().rotate(90)
        ui.iconScannerLite = QPixmap(os.path.join(os.path.dirname(__file__), "assets/logo_scanner_lite.png")).transformed(rotate90, Qt.SmoothTransformation)
        ui.iconScanner = QPixmap(os.path.join(os.path.dirname(__file__), "assets/logo_scanner.png")).transformed(rotate90, Qt.SmoothTransformation)
        ui.iconPlatform = QPixmap(os.path.join(os.path.dirname(__file__), "assets/logo_platform.png")).transformed(rotate90, Qt.SmoothTransformation)
        ui.iconLinuxPlatform = QPixmap(os.path.join(os.path.dirname(__file__), "assets/logo_linux_platform.png")).transformed(rotate90, Qt.SmoothTransformation)
        ui.coming_soon = QPixmap(os.path.join(os.path.dirname(__file__), "assets/coming_soon.png"))

        ui.setWindowIcon(ui.icon)

        ui.tabMode.setTabIcon(0,ui.iconScannerLite)
        ui.tabMode.setTabIcon(1,ui.iconScanner)
        ui.tabMode.setTabIcon(2,ui.iconPlatform)
        ui.tabMode.setTabIcon(3,ui.iconLinuxPlatform)
        
        ui.tabMode.setIconSize(QSize(80, 80)) 

        ui.logoSoon1.setPixmap(ui.coming_soon)
        ui.logoSoon2.setPixmap(ui.coming_soon)
        ui.logoSoon3.setPixmap(ui.coming_soon)

        #ui.logoSoon.setIconSize(QSize(80, 80)) 

        file.close()
        return ui

    def getUI(self):
        return self.ui

    def connectEvents(self):
        self.ui.actQuit.triggered.connect(self.actQuit)
        self.ui.actI2cxWebsite.triggered.connect(self.actI2cxWebsite)
        self.ui.actLootusWebsite.triggered.connect(self.actLootusWebsite)

    def indexChanged(self,value):
        self.ui.tabMode.setCurrentIndex(value)
   
    def actI2cxWebsite(self):
        QtGui.QDesktopServices.openUrl(QUrl("https://i2cx.io"))
    
    def actLootusWebsite(self):
        QtGui.QDesktopServices.openUrl(QUrl("https://www.lootus.net"))

    def actQuit(self):
        quit()

    def lowByte(number):
        return number & 0xFF

    def highByte(number):
        return (number>>8) & 0xff

    def Byte0(number):
        return number & 0xFF
    
    def Byte1(number):
        return (number>>8) & 0xff

    def Byte2(number):
        return (number>>16) & 0xff
    
    def Byte3(number):
        return (number>>24) & 0xff

    def isHex(s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False