from logging import exception
import sys
sys.path.append(".")

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,QThreadPool,QObject,Slot,QRectF
from PySide6.QtWidgets import QApplication,QTabBar,QTabWidget,QWidget,QStylePainter,QStyleOptionTab,QStyle
from PySide6.QtCore import Qt 

from PySide6.QtWidgets import QProxyStyle
import importlib
import os

from i2cx.core import Core
from i2cx.plugins.i2c import I2c
from i2cx.plugins.spi import Spi
from i2cx.plugins.uart import Uart

from pyftdi.ftdi import Ftdi

class Cli:
    def __init__(self):
        self.app = QApplication(sys.argv)
        loader = QUiLoader()

        # #Load Core QMainWindow
        self.core = Core(self.app)
        self.ui = self.core.getUI()

        self.ui.setFixedSize(1000, 600)
        self.ui.threadpool = QThreadPool()

        #Load Plugins
        self.formI2C = I2c(self.ui)
        self.i2cUI = self.formI2C.getUI()

        self.formSPI = Spi(self.ui)
        self.spiUI = self.formSPI.getUI()

        self.formUART = Uart(self.ui)
        self.uartUI = self.formUART.getUI()

        self.app.aboutToQuit.connect(self.exitHandler)
        
        Ftdi.add_custom_product(Ftdi.DEFAULT_VENDOR, 0x6E50,"i2cx-scanner-lite")
        
        self.ui.show()
        self.app.exec_()

    def exitHandler(self):
        self.formI2C.close()   
        self.formSPI.close()    
        self.formUART.close() 
        
if __name__ == '__main__':
    Cli()