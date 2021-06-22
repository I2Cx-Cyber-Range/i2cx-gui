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

import sys
import binascii
import traceback
import threading

class spiGetExtendedID :
    def __init__(self,parent):
        self.mainUI = parent.mainUI
        self.ui = parent.ui
        self.parent = parent
        self.eventStop = threading.Event()

    def action(self):
        try :
            # Get Port from static variable in Core Class
            portURL = Core.BASE_URL+str(self.ui.cbxPort.currentData())
            frequency = self.ui.cbxFrequency.currentData()
            mode = self.ui.cbxMode.currentData()
            cs = self.ui.cbxCS.currentData()

            port = self.parent.getSPI(port=portURL)
            slave = port.get_port(freq=frequency,cs=cs,mode=mode)

            jedec_id = slave.exchange([0x9f], 3+17)
            ID = binascii.hexlify(jedec_id).decode("utf-8").upper()

            self.ui.txtDeviceID.clear()
            self.ui.txtDeviceID.insertPlainText(ID)

            port.close()

        except Exception as e:
            print(e)
            if e.__class__  == FtdiError: 
                MessageBoxError("I²Cx Scanner Lite port is already used, please change the port.",self.parent)
            
            elif e.__class__  == UsbToolsError:
                MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
            
            elif e.__class__  == USBError:
                MessageBoxError("I²Cx Scanner Lite can't be found, please connect the board.",self.parent)
        
            else:
                traceback.print_exc()
                MessageBoxError("Get extended ID failed.",self)
            
 
    def close(self):
        return