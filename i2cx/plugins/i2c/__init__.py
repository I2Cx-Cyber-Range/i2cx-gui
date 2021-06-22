import sys
sys.path.append(".")

from math import ceil

from i2cx.plugins.i2c.i2cScan import i2cScan
from i2cx.plugins.i2c.i2cErase import i2cErase
from i2cx.plugins.i2c.i2cReadToDataview import i2cReadToDataview
from i2cx.plugins.i2c.i2cWriteFromDataview import i2cWriteFromDataview
from i2cx.plugins.i2c.i2cReadToFile import i2cReadToFile
from i2cx.plugins.i2c.i2cWriteFromFile import i2cWriteFromFile


from logging import exception
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Signal, Slot
from PySide6.QtWidgets import QTableView,QTableWidgetItem, QFileDialog,QProgressDialog,QHeaderView
from PySide6.QtCore import Qt 
from PySide6.QtGui import QTextCursor,QFont
import threading
import os

from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError
from pyftdi.ftdi import Ftdi,FtdiError


from pyftdi.i2c import I2cController

from i2cx.core import Core
from i2cx.core.Worker import Worker
from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.ProgressDialog import ProgressDialog


class I2c:
    def __init__(self,ui):
        self.mainUI = ui
        self.pluginName = "I2C"
        self.ui = self.loadUI()
        self.populateUI()
        self.connectEvents()  

        self.eventStop = threading.Event()
        self.eventStop = threading.Event()
        self.eventStop = threading.Event()
        self.eventStop = threading.Event()

    def loadUI(self):
        loader = QUiLoader()
        file = QFile(os.path.join(os.path.dirname(__file__), "gui/gui.ui"))
        file.open(QFile.ReadOnly)
        ui = loader.load(file)        
        self.mainUI.tabWidget.addTab(ui,self.pluginName)
        return ui

    def populateUI(self):
        #Port Selection
        self.ui.cbxPort.addItem("Port A",1)
        self.ui.cbxPort.addItem("Port B",2)

        #Frequency
        self.ui.cbxFrequency.addItem("100 Khz",100000)
        self.ui.cbxFrequency.addItem("400 Khz",400000)
        self.ui.cbxFrequency.addItem("1 Mhz",1000000)

        #Page Size
        self.ui.cbxPageSize.addItem("8 Bytes",8)
        self.ui.cbxPageSize.addItem("16 Bytes",16)
        self.ui.cbxPageSize.addItem("32 Bytes",32)
        self.ui.cbxPageSize.addItem("64 Bytes",64)
        self.ui.cbxPageSize.addItem("128 Bytes",128)
        self.ui.cbxPageSize.addItem("256 Bytes",256)
        self.ui.cbxPageSize.addItem("512 Bytes",512)
        self.ui.cbxPageSize.addItem("1 KBytes",1024)

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

        self.createColumnDataView(self.ui.tblDataView)
       

    def createColumnDataView(self,dataview):
        columnLabels = ["Address","0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","ASCCI"]
        dataview.setColumnCount(len(columnLabels))
        dataview.setHorizontalHeaderLabels(columnLabels)
        #dataview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #dataview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        dataview.setMinimumWidth(0)
        header = dataview.horizontalHeader()   
       
        for i in range (0,len(columnLabels)):
            if i == 0:
                header.setSectionResizeMode(QHeaderView.Fixed)
                dataview.setColumnWidth(i, 100)
            elif i == (len(columnLabels)-1):
                header.setSectionResizeMode(QHeaderView.Fixed)
                dataview.setColumnWidth(i, 150)
            else:
                header.setSectionResizeMode(QHeaderView.Fixed)
                dataview.setColumnWidth(i, 30)        

    def getUI(self):
        return self.ui

    def getI2C(self,port,frequency):
        i2c = I2cController()
        i2c.set_retry_count(1)
        i2c.configure(port,frequency=frequency)
        return i2c

    def connectEvents(self):

        self.erase = i2cErase(self)
        self.ui.btnErase.clicked.connect(self.erase.action)
           
        self.scan = i2cScan(self)
        self.ui.btnScan.clicked.connect(self.scan.action)

        self.readToFile = i2cReadToFile(self)
        self.ui.btnReadToFile.clicked.connect(self.readToFile.action)

        self.readToDataView = i2cReadToDataview(self)
        self.ui.btnReadToDataview.clicked.connect(self.readToDataView.action)

        self.writeFromDataview = i2cWriteFromDataview(self)
        self.ui.btnWriteFromDataview.clicked.connect(self.writeFromDataview.action)
        
        self.writeFromFile = i2cWriteFromFile(self)
        self.ui.btnWriteFromFile.clicked.connect(self.writeFromFile.action)

        self.ui.cbxTotalSize.activated.connect(self.fillEmptyDataview)
        self.fillEmptyDataview() #load firsttime

        self.ui.tblDataView.itemChanged.connect(self.itemChanged)

    def itemChanged(self,Qitem):
        row = Qitem.row()
        column = Qitem.column()

        if column != 0 and column != 17 :
            if Core.isHex(Qitem.text()) and (len(Qitem.text()) <= 2):
                intValue = int(Qitem.text(), 16)
                value = str.format('{:02X}', intValue).upper()
                Qitem.setText(value)
                Qitem.setData(Qt.UserRole,value)
               
                if self.ui.tblDataView.item(row,17) is not None:
                    currentString = list(self.ui.tblDataView.item(row,17).text())

                    if (intValue >= 0x20) and (intValue < 0x7F):
                        currentString[column-1] = chr(intValue)
                    else:
                        currentString[column-1] = '.' 
                
                    self.ui.tblDataView.item(row,17).setText(''.join(currentString))
                
            else:
                MessageBoxError("Wrong hexadecimal byte value, hex need to be in format 00 to FF (0-9,A-F)",self)
                Qitem.setText(Qitem.data(Qt.UserRole))


    def fillEmptyDataview(self):
        data = ["0x00000000","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","FF","................"]
        totalSize = self.ui.cbxTotalSize.currentData()
        nbRow = ceil(totalSize/16)
        self.ui.tblDataView.setRowCount(0)
        for i in range(0,nbRow):
            #padding to 8 digits
            data[0] = "{0:#0{1}X}".format(i*16,10)
            self.addTableRow(self.ui.tblDataView, data)
            
    def addTableRow(self, table, row_data):
        row = table.rowCount()
        table.setRowCount(row+1)
        col = 0

        i=0
        for item in row_data:
            cell = QTableWidgetItem(str(item))
            cell.setTextAlignment( Qt.AlignCenter )
            cell.setData(Qt.UserRole ,str(item))
            if (i == 0) or (i == 17):
                cell.setFlags(Qt.NoItemFlags | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            else:
                cell.setFlags(Qt.NoItemFlags | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
            table.setItem(row, col, cell)
            col += 1

            i = i + 1   
    

    def close(self):
        self.readToDataView.close()
        self.writeFromDataview.close()
        self.erase.close()
        self.scan.close()
        self.readToFile.close()
        self.writeFromFile.close()

    