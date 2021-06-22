from PySide6.QtWidgets import QTableWidgetItem,QFileDialog
from PySide6.QtCore import Qt 

from i2cx.core import Core
from i2cx.core.Worker import Worker
from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.ProgressDialog import ProgressDialog

from pyftdi.i2c import I2cNackError

from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError
from pyftdi.ftdi import Ftdi,FtdiError

import threading

class i2cScan :
    def __init__(self,parent):
        self.mainUI = parent.mainUI
        self.ui = parent.ui
        self.parent = parent
        self.eventStop = threading.Event()

    def action(self):
        try :
            self.completeError = False
            
            self.eventStop.clear()
            
            self.progressDialog = ProgressDialog("Scan I2C in progress",self.parent)

            # Get Port from static variable in Core Class
            port = Core.BASE_URL+str(self.ui.cbxPort.currentData())
            frequency=self.ui.cbxFrequency.currentData()

            # Pass the function to execute
            worker = Worker(self.workerJob,port=port,frequency=frequency) # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.resultCallback)
            worker.signals.finished.connect(self.completeCallback)
            worker.signals.progress.connect(self.progressCallback)
            worker.signals.data.connect(self.dataCallBack)
            worker.signals.error.connect(self.errorCallback)

            # Execute worker from threadpool of main application
            self.mainUI.threadpool.start(worker)

        except Exception as e: 
           print(e)
           MessageBoxError("Scan failed.",self.parent)


    def workerJob(self,progress_callback,data_callback,port,frequency):
        i2c = self.parent.getI2C(port,frequency)
        # Get a port to an I2C slave device
        result = []
        for addr in range(i2c.HIGHEST_I2C_ADDRESS + 1):
            port  = i2c.get_port(addr)
            progress_callback.emit(addr*100/127) #Percentage 127 addresses to scan
            try:
                port.read_from(0x00, 1)  
                result.append(addr)
                #Stop worker from progressBar
                if self.eventStop.is_set() :
                    return result               
            except I2cNackError:
                continue
        i2c.close()
        return result
        
    def resultCallback(self,result):
        if self.progressDialog.wasCanceled():
            MessageBoxWarning("Scanning was cancelled.",self)
        else:
            if(result != None):
                self.ui.tblBusScan.setRowCount(0)
                for currentResult in result:
                    # Add an item at the end of table
                    self.ui.tblBusScan.insertRow(self.ui.tblBusScan.rowCount())
                    item = QTableWidgetItem(hex(currentResult))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.ui.tblBusScan.setItem(self.ui.tblBusScan.rowCount()-1, 0, item) 
            else:
                MessageBoxError("Scanning failed.",self)

    def completeCallback(self):
        return

    def progressCallback(self,percentage):
        self.progressDialog.setValue(percentage)   
        if self.progressDialog.wasCanceled():
            self.eventStop.set()

    def dataCallBack(self,data):
        return

    def errorCallback(self,error):
        self.completeError = True
        self.progressDialog.cancel()
        exctype = error[0]

        if exctype == FtdiError:  #and   #No USB device matches URL
            MessageBoxError("I²Cx Scanner Lite port is already used, please change the port.",self.parent)
            
        elif exctype == UsbToolsError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
        
        elif exctype == USBError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
        
        else:
            MessageBoxError("Scanning failed.",self)
            #value
            #print("errorValue" + error[1])
            #tracebackValue
            print(error[2])

    def close(self):
        self.eventStop.set()