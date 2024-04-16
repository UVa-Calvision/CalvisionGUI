from PyQt5.QtCore import *
from PyDecode import *
import subprocess
import time
import sys
import os

class Worker_startDecode(QObject):
    finished = pyqtSignal()
    # update_log_file_name = pyqtSignal(str)
    # plot_bin = pyqtSignal()

    def __init__(self,  fileSend, numDevices, chnl_names):
        super(Worker_startDecode, self).__init__()
        filename = 'PyDecode.py'
        self.arrCall = ["python3", filename, fileSend, numDevices]
        self.file_name = fileSend
        self.numDevices = numDevices
        self.chnl_names = chnl_names

    def run(self):  
        print("Decode started!")
        #filepath = os.path
        #filepath = os.path.join(filepath)
        
        # if sys.platform == "win32":
        #     os.startfile(filename)
        # else:
        #     #opener = "open" if sys.platform == "darwin" else ""
        #     subprocess.run(self.arrCall)

        self.decode = PyDeocde(self.file_name, int(self.numDevices), self.chnl_names)
        self.decode.start(self.file_name)

    
    def finish(self):
        self.decode.close()
        self.finished.emit()

