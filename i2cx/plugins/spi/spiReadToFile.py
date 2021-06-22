from PySide6.QtWidgets import QTableWidgetItem,QFileDialog
from PySide6.QtCore import Qt 

from i2cx.core import Core
from i2cx.core.Worker import Worker
from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.ProgressDialog import ProgressDialog


import os

from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError
from pyftdi.ftdi import Ftdi,FtdiError

import threading

class spiReadToFile :
    def __init__(self,parent):
        self.mainUI = parent.mainUI
        self.ui = parent.ui
        self.parent = parent
        self.eventStop = threading.Event()
     
    def action(self):
        try :
            self.completeError = False
            self.eventStop.clear()
           
            filePath,fileType = QFileDialog.getSaveFileName(self.ui, 'Select a destination file',os.path.expanduser("~/Desktop"))
            if filePath == '':
                MessageBoxWarning("Bad filename, please, specify a new filename.",self.parent)
            else:
                pageSize  = self.ui.cbxPageSize.currentData()
                totalSize = self.ui.cbxTotalSize.currentData()

                # Get Port from static variable in Core Class
                portURL = Core.BASE_URL+str(self.ui.cbxPort.currentData())
                frequency = self.ui.cbxFrequency.currentData()
                mode = self.ui.cbxMode.currentData()
                cs = self.ui.cbxCS.currentData()

                self.port = self.parent.getSPI(port=portURL)
                slave = self.port.get_port(freq=frequency,cs=cs,mode=mode)

                self.progressDialog = ProgressDialog("Read SPI in progress",self.parent)

                # Pass the function to execute
                worker = Worker(self.workerJob,slave=slave,filePath=filePath,pageSize=pageSize,totalSize=totalSize) # Any other args, kwargs are passed to the run function
                worker.signals.result.connect(self.resultCallback)
                worker.signals.finished.connect(self.completeCallback)
                worker.signals.progress.connect(self.progressCallback)
                worker.signals.data.connect(self.dataCallback)
                worker.signals.error.connect(self.errorCallback)

                # Execute worker from threadpool of main application
                self.mainUI.threadpool.start(worker)

        except Exception as e: 
           print(e)
           MessageBoxError("Reading failed.",self)

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
            MessageBoxError("Reading failed.",self.parent)
            #tracebackValue
            print(error[2])


    def completeCallback(self):
        try:
            self.port.close()
        finally:
            if self.eventStop.is_set():
                self.progressDialog.cancel()
                MessageBoxWarning("Reading was cancelled",self.parent)
            elif self.completeError == False:
                self.progressDialog.cancel()
                MessageBoxInformation("Data is saved in the selected file.",self.parent)

    def progressCallback(self,percentage):
        self.progressDialog.setValue(percentage)   
        if self.progressDialog.wasCanceled():
            self.eventStop.set()

    def workerJob(self,progress_callback,data_callback,slave,filePath,pageSize,totalSize):
        pageCount = int(totalSize/pageSize)

        dataFile=open(filePath,'wb')
        for i in range(0, pageCount):
            #Stop worker from progressBar
            if self.eventStop.is_set() :
                return filePath   

            memAddress = i*pageSize

            if totalSize > 2^24 : 
                #Prepare read command with 32bits addresses
                readCommand = [0x03,Core.Byte3(memAddress),Core.Byte2(memAddress),Core.Byte1(memAddress),Core.Byte0(memAddress)]
            elif totalSize > 2^16 : 
                #Prepare read command with 24bits addresses
                readCommand = [0x03,Core.Byte2(memAddress),Core.Byte1(memAddress),Core.Byte0(memAddress)]
            elif totalSize > 2^8 : 
                #Prepare read command with 16bits addresses
                readCommand = [0x03,Core.Byte1(memAddress),Core.Byte0(memAddress)]
            else:
                #Prepare read command with 8bits addresses
                readCommand = [0x03,Core.Byte0(memAddress)]

            receivedData = slave.exchange(readCommand,pageSize)

            dataFile.write(receivedData)
            progress_callback.emit((i+1)*100/pageCount) #Percentage 
        dataFile.close()

        self.port.close()

        return filePath

    def close(self):
        self.eventStop.set()