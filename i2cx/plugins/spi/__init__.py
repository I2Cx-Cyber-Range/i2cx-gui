import sys
sys.path.append(".")



from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from pyftdi.spi import SpiController
import os
from pyftdi.usbtools import UsbTools, UsbToolsError
from PySide6.QtWidgets import QHeaderView,QTableWidgetItem

from math import ceil


from i2cx.core.MessageBox import MessageBoxError

from PySide6.QtCore import Qt 
from i2cx.core import Core
from i2cx.plugins.spi.spiGetID import spiGetID
from i2cx.plugins.spi.spiGetExtendedID import spiGetExtendedID
from i2cx.plugins.spi.spiReadToFile import spiReadToFile
from i2cx.plugins.spi.spiWriteFromFile import spiWriteFromFile
from i2cx.plugins.spi.spiErase import spiErase


class Spi:
    def __init__(self,ui):
        self.mainUI = ui
        self.pluginName = "SPI"
        self.ui = self.loadUI()
        self.populateUI()
        self.connectEvents()

    def loadUI(self):
        loader = QUiLoader()
        file = QFile(os.path.join(os.path.dirname(__file__), "gui/gui.ui"))
        file.open(QFile.ReadOnly)
        localeUI = loader.load(file)
        self.mainUI.tabWidget.addTab(localeUI,self.pluginName)
        return localeUI

    def getUI(self):
        return self.ui

    def populateUI(self):
        #Port Selection
        self.ui.cbxPort.addItem("Port A",1)
        self.ui.cbxPort.addItem("Port B",2)

        #Frequency
        self.ui.cbxFrequency.addItem("1 Mhz",1E6)
        self.ui.cbxFrequency.addItem("2 Mhz",2E6)
        self.ui.cbxFrequency.addItem("4 Mhz",4E6)
        self.ui.cbxFrequency.addItem("8 Mhz",8E6)
        self.ui.cbxFrequency.addItem("16 Mhz",16E6)
        self.ui.cbxFrequency.addItem("32 Mhz",32E6)
        self.ui.cbxFrequency.addItem("50 Mhz",50E6)

        #Page Size
        self.ui.cbxPageSize.addItem("16 Bytes",16)
        self.ui.cbxPageSize.addItem("32 Bytes",32)
        self.ui.cbxPageSize.addItem("64 Bytes",64)
        self.ui.cbxPageSize.addItem("128 Bytes",128)
        self.ui.cbxPageSize.addItem("256 Bytes",256)
        self.ui.cbxPageSize.addItem("512 Bytes",512)
        self.ui.cbxPageSize.addItem("1 KBytes",1024)
        self.ui.cbxPageSize.addItem("2 KBytes",2*1024)
        self.ui.cbxPageSize.addItem("4 KBytes",4*1024)
        self.ui.cbxPageSize.addItem("8 KBytes",8*1024)
        self.ui.cbxPageSize.addItem("16 KBytes",16*1024)
        self.ui.cbxPageSize.addItem("32 KBytes",32*1024)
        self.ui.cbxPageSize.addItem("64 KBytes",64*1024)
        self.ui.cbxPageSize.addItem("128 KBytes",128*1024)

        #Mode
        self.ui.cbxMode.addItem("Mode 0",0)
        self.ui.cbxMode.addItem("Mode 2",2)

        #Chip select
        self.ui.cbxCS.addItem("CS 0",0)
        self.ui.cbxCS.addItem("CS 1",1)
        self.ui.cbxCS.addItem("CS 2",2)
        self.ui.cbxCS.addItem("CS 3",3)
        self.ui.cbxCS.addItem("CS 4",4)

        #Total size
        self.ui.cbxTotalSize.addItem("16 Bytes",16)
        self.ui.cbxTotalSize.addItem("32 Bytes",32)
        self.ui.cbxTotalSize.addItem("64 Bytes",64)
        self.ui.cbxTotalSize.addItem("128 Bytes",128)
        self.ui.cbxTotalSize.addItem("256 Bytes",256)
        self.ui.cbxTotalSize.addItem("512 Bytes",512)
        self.ui.cbxTotalSize.addItem("1 KBytes",1024)
        self.ui.cbxTotalSize.addItem("2 KBytes",1024*2)
        self.ui.cbxTotalSize.addItem("4 KBytes",1024*4)
        self.ui.cbxTotalSize.addItem("8 KBytes",1024*8)
        self.ui.cbxTotalSize.addItem("16 KBytes",1024*16)
        self.ui.cbxTotalSize.addItem("32 KBytes",1024*32)
        self.ui.cbxTotalSize.addItem("64 KBytes",1024*64)

        self.ui.cbxTotalSize.addItem("1 MBytes",1*1024*1024)
        self.ui.cbxTotalSize.addItem("2 MBytes",2*1024*1024)
        self.ui.cbxTotalSize.addItem("4 MBytes",4*1024*1024)
        self.ui.cbxTotalSize.addItem("8 MBytes",8*1024*1024)
        self.ui.cbxTotalSize.addItem("16 MBytes",16*1024*1024)
        self.ui.cbxTotalSize.addItem("32 MBytes",32*1024*1024)
        self.ui.cbxTotalSize.addItem("64 MBytes",64*1024*1024)
        self.ui.cbxTotalSize.addItem("128 MBytes",128*1024*1024)
        self.ui.cbxTotalSize.addItem("256 MBytes",256*1024*1024)


    def getSPI(self,port):
        spi = SpiController()
        spi.configure(port,cs_count=5)
        return spi
        
    def connectEvents(self):
        self.getID = spiGetID(self)
        self.ui.btnGetID.clicked.connect(self.getID.action)

        self.getExtendedID = spiGetExtendedID(self)
        self.ui.btnGetExtendedID.clicked.connect(self.getExtendedID.action)

        self.readToFile = spiReadToFile(self)
        self.ui.btnReadToFile.clicked.connect(self.readToFile.action)

        self.writeFromFile = spiWriteFromFile(self)
        self.ui.btnWriteFromFile.clicked.connect(self.writeFromFile.action)

        self.erase = spiErase(self)
        self.ui.btnErase.clicked.connect(self.erase.action)



    def close(self):
        self.getID.close()
        self.getExtendedID.close()

