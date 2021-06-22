from logging import exception
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

import threading
import os
import sys
import time
import traceback

sys.path.append(".")
from pyftdi.ftdi import Ftdi

from i2cx.core.Worker import Worker

from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.ProgressDialog import ProgressDialog

from i2cx.core import Core

from pyftdi.ftdi import Ftdi,FtdiError

import threading

import pyftdi.serialext
from serial import SerialException
from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError

class Uart:
    def __init__(self,ui):
        self.mainUI = ui
        self.pluginName = "UART"
        self.ui = self.loadUI()
        self.connectEvents()
        self.populateUI()

        self.connectEventStop = threading.Event()

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
        self.ui.btnConnect.setEnabled(True) 
        self.ui.btnDisconnect.setEnabled(False) 

        self.ui.btnSendAsText.setEnabled(False) 
        self.ui.btnSendAsHex.setEnabled(False) 


        #Port Selection
        self.ui.cbxPort.addItem("Port A",1)
        self.ui.cbxPort.addItem("Port B",2)

        #Port BaudRate
        self.ui.cbxBaudRate.addItem("1 200",1200)
        self.ui.cbxBaudRate.addItem("2 400",2400)
        self.ui.cbxBaudRate.addItem("4 800",4800)
        self.ui.cbxBaudRate.addItem("9 600",9600)
        self.ui.cbxBaudRate.addItem("19 200",19200)
        self.ui.cbxBaudRate.addItem("38 400",38400)
        self.ui.cbxBaudRate.addItem("57 600",57600)
        self.ui.cbxBaudRate.addItem("115 200",115200)
        self.ui.cbxBaudRate.addItem("230 400",230400)
        self.ui.cbxBaudRate.addItem("460 800",460800)
        self.ui.cbxBaudRate.addItem("921 600",921600)
        self.ui.cbxBaudRate.addItem("1 843 200",1843200)

        # Default 9600
        self.ui.cbxBaudRate.setCurrentIndex(7)

        #Port Word Size
        self.ui.cbxWordSize.addItem("7",7)
        self.ui.cbxWordSize.addItem("8",8)
        # Default 8
        self.ui.cbxWordSize.setCurrentIndex(1)

        #Port Parity
        self.ui.cbxParity.addItem("NONE","N")
        self.ui.cbxParity.addItem("EVEN","E")
        self.ui.cbxParity.addItem("ODD","O")
        
        #Port Stop Bit
        self.ui.cbxStopBit.addItem("1",1)
        self.ui.cbxStopBit.addItem("1.5",1.5)
        self.ui.cbxStopBit.addItem("2",2)

    def getUART(self,port,byteSize,stopBits,parity,rtsCts,dsrDtr,baudRate):
        uart = pyftdi.serialext.serial_for_url("ftdi://ftdi:i2cx-scanner-lite/"+str(self.ui.cbxPort.currentData()), bytesize=byteSize, stopbits=stopBits,parity=parity,rtscts=rtsCts,dsrdtr=dsrDtr,timeout=0, baudrate=baudRate)  
        return uart

    def connectEvents(self):
        self.ui.btnSendAsHex.clicked.connect(self.btnSendAsHex)
        self.ui.btnSendAsText.clicked.connect(self.btnSendAsText)
        self.ui.btnClear.clicked.connect(self.btnClear)
        self.ui.btnConnect.clicked.connect(self.btnConnect)
        self.ui.btnDisconnect.clicked.connect(self.btnDisconnect)
    
    def btnClear(self):
        self.ui.txtConsole.clear()

    def btnConnect(self):
        try:
            self.connectEventStop.clear()
            
            # Get Port from static variable in Core Class
            port = Core.BASE_URL+str(self.ui.cbxPort.currentData())
            bytesize=self.ui.cbxWordSize.currentData()
            stopbits=self.ui.cbxStopBit.currentData()
            parity=self.ui.cbxParity.currentData()
            rtscts=False
            dsrdtr=False
            baudrate=self.ui.cbxBaudRate.currentData()
            self.uart = self.getUART(port,bytesize,stopbits,parity,rtscts,dsrdtr,baudrate)

            # Pass the function to execute, Any other args, kwargs are passed to the run function
            worker = Worker(self.connectWorker,uart=self.uart) 
            #worker.signals.result.connect(self.connectResult)
            worker.signals.finished.connect(self.connectComplete)
            worker.signals.progress.connect(self.connectProgress)
            worker.signals.error.connect(self.connectError)
            worker.signals.data.connect(self.connectData)

            # Execute worker from threadpool of main application
            self.mainUI.threadpool.start(worker)

            self.ui.btnConnect.setEnabled(False) 
            self.ui.btnDisconnect.setEnabled(True) 

            self.ui.btnSendAsText.setEnabled(True) 
            self.ui.btnSendAsHex.setEnabled(True) 

            self.ui.cbxPort.setEnabled(False) 
            self.ui.cbxBaudRate.setEnabled(False) 
            self.ui.cbxWordSize.setEnabled(False) 
            self.ui.cbxParity.setEnabled(False) 
            self.ui.cbxStopBit.setEnabled(False) 

        except :
            exctype, value = sys.exc_info()[:2]
            if exctype == FtdiError:  #and   #No USB device matches URL
                MessageBoxError("I²Cx Scanner Lite port is already used, please change the port.",self)
                
            if exctype == UsbToolsError:
                MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self)
            
            if exctype == USBError:
                MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self)

            if exctype == SerialException:
                 MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self)
           
            else:
                traceback.print_exc()
                MessageBoxError("Connecting UART failed.",self)

    def connectProgress(self):
        return

    def btnDisconnect(self):
        self.connectEventStop.set()

    def connectComplete(self):
        self.ui.btnConnect.setEnabled(True) 
        self.ui.btnDisconnect.setEnabled(False) 

        self.ui.btnSendAsText.setEnabled(False) 
        self.ui.btnSendAsHex.setEnabled(False) 

        self.ui.cbxPort.setEnabled(True) 
        self.ui.cbxBaudRate.setEnabled(True) 
        self.ui.cbxWordSize.setEnabled(True) 
        self.ui.cbxParity.setEnabled(True) 
        self.ui.cbxStopBit.setEnabled(True) 

    def connectWorker(self,progress_callback,data_callback,uart):
        while not self.connectEventStop.is_set() :
            data = uart.read(4096)
            if not data : 
                continue

            data_callback.emit(data)        
            time.sleep(0.1)

        self.uart.close()

    def connectError(self,error):
        self.uart.close()
        exctype = error[0]

        if exctype == FtdiError:  #and   #No USB device matches URL
            MessageBoxError("I²Cx Scanner Lite can't be found or port is already used, please reconnect or change the port.",self)
            
        if exctype == UsbToolsError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self)
           
        if exctype == USBError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self)

        else:
            MessageBoxError("Connecting UART failed.",self)
            #tracebackValue
            print(error[2])
            #print(error[1])

    def connectData(self,data):
        try:
            self.ui.txtConsole.insertPlainText(data.decode("utf-8"))
            self.ui.txtConsole.verticalScrollBar().setValue(self.ui.txtConsole.verticalScrollBar().maximum())
        except :
            return


    def btnSendAsHex(self):
        data= self.ui.txtValue.toPlainText().split()

        dataToSend = []
        for byte in data:
            if Core.isHex(byte) :
                dataToSend.append(int(byte, 16))
            else:
                MessageBoxError(f"'{byte}' is a wrong hexadecimal byte value, hex need to be in format 00 to FF (0-9,A-F)",self)
                return

        if self.uart.is_open:
            if self.ui.rbCR.isChecked():
                dataToSend.append(0x0D)
            elif self.ui.rbLF.isChecked():
                dataToSend.append(0x0A)
            elif self.ui.rbCRLF.isChecked():
                dataToSend.append(0x0D)
                dataToSend.append(0x0A)

            dataToSend = bytes(dataToSend)
            self.uart.write(dataToSend)


    def btnSendAsText(self):
        if self.uart.is_open:
            data= self.ui.txtValue.toPlainText()
            if self.ui.rbCR.isChecked():
                data = data + "\r"
            elif self.ui.rbLF.isChecked():
                data = data + "\n"
            elif self.ui.rbCRLF.isChecked():
                data = data + "\r\n"

            uartDATA = bytes(data,'utf-8')
            self.uart.write(uartDATA)
    
    def close(self):
        self.connectEventStop.set()
