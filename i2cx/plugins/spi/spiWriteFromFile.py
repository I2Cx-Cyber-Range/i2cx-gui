from PySide6.QtWidgets import QTableWidgetItem,QFileDialog,QMessageBox
from PySide6.QtCore import Qt 

from i2cx.core import Core
from i2cx.core.Worker import Worker
from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.MessageBox import MessageBoxConfirmation

from i2cx.core.ProgressDialog import ProgressDialog


import os,time

from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError
from pyftdi.ftdi import Ftdi,FtdiError

import threading

class spiWriteFromFile :
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
            
    
                filePath,fileType = QFileDialog.getOpenFileName(self.ui, 'Select a file',os.path.expanduser("~/Desktop"))
                if filePath == '':
                    MessageBoxWarning("Bad filename, please, specify a new filename.",self.parent)
                else:
        
                    pageSize  = self.ui.cbxPageSize.currentData()
                    totalSize = self.ui.cbxTotalSize.currentData()
                    frequency = self.ui.cbxFrequency.currentData()

                    if os.path.getsize(filePath) != totalSize:
                        MessageBoxError("Wrong size, the file size must be egal to total size of device.",self)
                    else:
                        self.writeProgressDialog = ProgressDialog("Writing in progress",self.parent)

                        # Get Port from static variable in Core Class
                        portURL = Core.BASE_URL+str(self.ui.cbxPort.currentData())
                       
                        mode = self.ui.cbxMode.currentData()
                        cs = self.ui.cbxCS.currentData()
                        self.port = self.parent.getSPI(port=portURL)
                        slave = self.port.get_port(freq=frequency,cs=cs,mode=mode)


                        # Pass the function to execute
                        worker = Worker(self.workerJob,slave=slave,filePath=filePath,pageSize=pageSize,totalSize=totalSize) # Any other args, kwargs are passed to the run function
                        worker.signals.result.connect(self.resultCallback)
                        worker.signals.finished.connect(self.completeCallback)
                        worker.signals.progress.connect(self.writeProgress)
                        worker.signals.data.connect(self.dataCallback)
                        worker.signals.error.connect(self.errorCallback)

                        # Execute worker from threadpool of main application
                        self.mainUI.threadpool.start(worker)

            except Exception as e: 
                print(e)
                MessageBoxError("Writing failed.",self)

    def dataCallback(self,data):
        return

    def resultCallback(self,result):
        return

    def errorCallback(self,error):
        self.completeError = True
        self.writeProgressDialog.cancel()
        exctype = error[0]


        if exctype == FtdiError:
            MessageBoxError("I²Cx Scanner Lite port is already used, please change the port.",self.parent)
            
        elif exctype == UsbToolsError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
            
        elif exctype == USBError:
            MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
        
        else:
            #tracebackValue
            print(error[2])
            MessageBoxError("Writing failed.",self.parent)
           

    def completeCallback(self):
        try:
            self.port.close()
        finally:
            if self.eventStop.is_set():
                MessageBoxWarning("Writing was cancelled",self.parent)
            elif self.completeError == False:
                MessageBoxInformation("Data is saved in selected file.",self.parent)

    def writeProgress(self,percentage):
        self.writeProgressDialog.setValue(percentage)   
        if self.writeProgressDialog.wasCanceled():
            self.eventStop.set()

    def workerJob(self,progress_callback,data_callback,slave,filePath,pageSize,totalSize):
        pageCount = int(totalSize/pageSize)

        with open(filePath, "rb") as f:
            i = 0
            bytes_read = f.read(pageSize)
            while bytes_read:
                #Stop worker from progressBar
                if self.eventStop.is_set() :
                    return filePath   

                memAddress = i*pageSize
                if totalSize > 2^24 : 
                    #Prepare read command with 32bits addresses
                    writeCommand = [0x02,Core.Byte3(memAddress),Core.Byte2(memAddress),Core.Byte1(memAddress),Core.Byte0(memAddress)]
                elif totalSize > 2^16 : 
                    #Prepare read command with 24bits addresses
                    writeCommand = [0x02,Core.Byte2(memAddress),Core.Byte1(memAddress),Core.Byte0(memAddress)]
                elif totalSize > 2^8 : 
                    #Prepare read command with 16bits addresses
                    writeCommand = [0x02,Core.Byte1(memAddress),Core.Byte0(memAddress)]
                else:
                    #Prepare read command with 8bits addresses
                    writeCommand = [0x02,Core.Byte0(memAddress)]

                #Enable write command
                slave.exchange([0x06],0)
                
                slave.exchange(writeCommand,0)

                self.waitBusy(slave)
                progress_callback.emit((i+1)*100/pageCount) #Percentage 

                i = i + 1 
                bytes_read = f.read(pageSize)
                
        return filePath


    def waitBusy(self,slave):
        busy = slave.exchange([0x05],1)[0] 
        while (busy & 0x1) == 1 :
            time.sleep(0.001)
            busy = slave.exchange([0x05],1)[0]

    def close(self):
        self.eventStop.set()
