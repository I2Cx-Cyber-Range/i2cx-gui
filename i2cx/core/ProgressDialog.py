from PySide6.QtWidgets import ( QMessageBox,QProgressDialog)
from PySide6.QtCore import Qt 

class ProgressDialog(QProgressDialog):
    def __init__(self,message,parent):
        super(ProgressDialog, self).__init__(message, "Abort", 0, 100, parent.mainUI)
        self.setWindowTitle(parent.pluginName)
        self.setWindowIcon(parent.mainUI.icon)
        self.setWindowModality(Qt.WindowModal)
        self.show()
