from PySide6.QtWidgets import QTableWidgetItem,QFileDialog,QMessageBox
from PySide6.QtCore import Qt 

from i2cx.core import Core
from i2cx.core.Worker import Worker
from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.MessageBox import MessageBoxConfirmation

from i2cx.core.ProgressDialog import ProgressDialog

from pyftdi.i2c import I2cNackError
import time

from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError
from pyftdi.ftdi import Ftdi,FtdiError

import threading

class i2cErase :
    def __init__(self,parent):
        self.mainUI = parent.mainUI
        self.ui = parent.ui
        self.parent = parent
        self.eventStop = threading.Event()
     

    def action(self):
        reply = MessageBoxConfirmation("Are you sure to overwrite data of selected device ?",self.parent)
        if reply.clickedButton() == reply.button(QMessageBox.Yes): 
            try :
                self.completeError = False
                self.eventStop.clear()
            
                selectedItem = self.ui.tblBusScan.currentItem() 
                if selectedItem  == None :
                    MessageBoxError("You need to launch a scan and select a device before.",self.parent)
                else:
                        pageSize  = self.ui.cbxPageSize.currentData()
                        totalSize = self.ui.cbxTotalSize.currentData()
                        selectedAddress = int(selectedItem.text(), 16)

                        self.progressDialog = ProgressDialog("Erase device in progress",self.parent)

                        # Get Port from static variable in Core Class
                        port = Core.BASE_URL+str(self.ui.cbxPort.currentData())
                        frequency=self.ui.cbxFrequency.currentData()

                        # Pass the function to execute
                        worker = Worker(self.workerJob,port=port,frequency=frequency,pageSize=pageSize,totalSize=totalSize,selectedAddress=selectedAddress) # Any other args, kwargs are passed to the run function
                        worker.signals.result.connect(self.resultCallback)
                        worker.signals.finished.connect(self.completeCallback)
                        worker.signals.progress.connect(self.progressCallback)
                        worker.signals.data.connect(self.dataCallback)
                        worker.signals.error.connect(self.errorCallback)

                        # Execute worker from threadpool of main application
                        self.mainUI.threadpool.start(worker)

            except Exception as e: 
                print(e)
                MessageBoxError("Erase failed.",self)

    def dataCallback(self,data):
        return

    def resultCallback(self,result):
        return

    def errorCallback(self,error):
        self.completeError = True
        self.progressDialog.cancel()
        exctype = error[0]
        if exctype == FtdiError:
            MessageBoxError("I²Cx Scanner Lite port is already used, please change the port.",self.parent)
            
        elif exctype == UsbToolsError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
            
        elif exctype == USBError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
        else:
            MessageBoxError("Erase failed.",self)
            #tracebackValue
            print(error[2])

    def completeCallback(self):
        if self.eventStop.is_set():
            self.progressDialog.close()
            MessageBoxWarning("Erase was cancelled.",self)
        elif self.completeError == False :
           MessageBoxInformation("Erase successful.",self)

    def progressCallback(self,percentage):
        self.progressDialog.setValue(percentage)   
        if self.progressDialog.wasCanceled():
            self.eventStop.set()

    def workerJob(self,progress_callback,data_callback,port,frequency,pageSize,totalSize,selectedAddress):
        i2c = self.parent.getI2C(port,frequency)
        slave = i2c.get_port(selectedAddress)  
        pageCount = int(totalSize/pageSize)

        # Create a buffer with pageSize buffer to erase
        dummy = [0xFF]*pageSize

        for i in range(0, pageCount):
            #Stop worker from progressBar
            if self.eventStop.is_set() :
                return 

            memAddress = i*pageSize
            if totalSize > 2048 : 
                #Prepare 16bits addresses
                toSend = [Core.highByte(memAddress),Core.lowByte(memAddress)]  + dummy
                slave. write(toSend) 
            else:
                #Prepare 8bits addresses
                toSend = [memAddress]  + dummy
                slave. write(toSend)

            self.waitBusy(slave)
            progress_callback.emit((i+1)*100/pageCount) #Percentage 

        i2c.close()
      

    def waitBusy(self,port):
        while True:
            time.sleep(0.001)
            try:
                port.read_from(0x00, 1)                 
                return True
            except I2cNackError:
                continue
    
    def close(self):
        self.eventStop.set()