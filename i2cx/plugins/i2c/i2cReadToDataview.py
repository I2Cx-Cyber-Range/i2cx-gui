from PySide6.QtWidgets import QTableWidgetItem,QFileDialog
from PySide6.QtCore import Qt 

from i2cx.core import Core
from i2cx.core.Worker import Worker
from i2cx.core.MessageBox import MessageBoxError
from i2cx.core.MessageBox import MessageBoxWarning
from i2cx.core.MessageBox import MessageBoxInformation
from i2cx.core.ProgressDialog import ProgressDialog


from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError
from pyftdi.ftdi import Ftdi,FtdiError

import threading

class i2cReadToDataview :
    def __init__(self,parent):
        self.mainUI = parent.mainUI
        self.ui = parent.ui
        self.parent = parent
        self.eventStop = threading.Event()

    def action(self):
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

                self.progressDialog = ProgressDialog("Read I2C in progress",self.parent)

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
           MessageBoxError("Reading failed.",self.parent)

    def resultCallback(self,result):
        return

    def dataCallback(self,data):
        self.fillDataview(data["data"],data["offset"])
        return

    def completeCallback(self):
        if self.eventStop.is_set():
            self.progressDialog.cancel()
            MessageBoxWarning("Reading was cancelled",self.parent)
        elif self.completeError == False:
            MessageBoxInformation("Data is available in dataview.",self)

    def progressCallback(self,percentage):
        self.progressDialog.setValue(percentage)   
        if self.progressDialog.wasCanceled():
            self.eventStop.set()

    def workerJob(self,progress_callback,data_callback,port,frequency,pageSize,totalSize,selectedAddress):
        i2c = self.parent.getI2C(port,frequency)
        slave = i2c.get_port(selectedAddress)  
        pageCount = int(totalSize/pageSize)

        for i in range(0, pageCount):
            #Stop worker from progressBar
            if self.eventStop.is_set() :
                return   

            memAddress = i*pageSize

            if totalSize > 2048 : 
                #Prepare 16bits addresses
                arrayAddress = [Core.highByte(memAddress),Core.lowByte(memAddress)]
            else:
                #Prepare 8bits addresses
                arrayAddress = [memAddress]
            
            receivedData = slave.exchange(arrayAddress, pageSize)
            
            data = dict()
            data["data"]   = receivedData
            data['offset'] = memAddress
            
            data_callback.emit(data) # send to GUI current receivedData
            progress_callback.emit((i+1)*100/pageCount) #Percentage 
        
        i2c.close()
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

    def fillDataview(self,data,offset):
        for i in range(0,len(data)):
            nbRow = int((i + offset) / 16)
            nbCol = int((i + offset) % 16) + 1 
            self.ui.tblDataView.item(nbRow, nbCol).setText("{0:0{1}X}".format(data[i],2))
            currentString = list(self.ui.tblDataView.item(nbRow,17).text())
            if (data[i] >= 0x20) and (data[i] < 0x7F):
                currentString[nbCol-1] = chr(data[i])
            else:
                currentString[nbCol-1] = '.' 
        
            self.ui.tblDataView.item(nbRow,17).setText(''.join(currentString))
   

    def close(self):
        self.eventStop.set()