from PySide6.QtWidgets import ( QMessageBox,QProgressDialog)

class MessageBoxError(QMessageBox):
    def __init__(self,message,parent):
        super(MessageBoxError, self).__init__()
        self.setWindowTitle("An error occured")
        self.setText(message)
        self.setDefaultButton(QMessageBox.Ok)
        self.setWindowIcon(parent.mainUI.icon)
        self.setIcon(QMessageBox.Critical)
        self.exec_()
        
class MessageBoxInformation(QMessageBox):
    def __init__(self,message,parent):
        super(MessageBoxInformation, self).__init__()
        self.setWindowTitle("Information")
        self.setText(message)
        self.setDefaultButton(QMessageBox.Ok)
        self.setWindowIcon(parent.mainUI.icon)
        self.setIcon(QMessageBox.Information)
        self.exec_()

class MessageBoxWarning(QMessageBox):
    def __init__(self,message,parent):
        super(MessageBoxWarning, self).__init__()
        self.setWindowTitle("Warning")
        self.setText(message)
        self.setDefaultButton(QMessageBox.Ok)
        self.setWindowIcon(parent.mainUI.icon)
        self.setIcon(QMessageBox.Warning)
        self.exec_()


class MessageBoxConfirmation(QMessageBox):
    def __init__(self,message,parent):
        super(MessageBoxConfirmation, self).__init__()
        self.setWindowTitle("Confirmation")
        self.setText(message)
        self.setStandardButtons(QMessageBox.Yes)
        self.addButton(QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        self.setWindowIcon(parent.mainUI.icon)
        self.setIcon(QMessageBox.Question)
        self.exec_()