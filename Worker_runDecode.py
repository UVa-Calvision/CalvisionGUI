from PyQt5.QtCore import *
import subprocess
import time
import sys
import os



class Worker_runDecode(QObject):
    finished = pyqtSignal()
    # update_log_file_name = pyqtSignal(str)
    # plot_bin = pyqtSignal()

    def __init__(self, file, numDevices):
        super(Worker_runDecode, self).__init__()
        filename = './decode.py'
        self.arrCall = ["python3", filename, file, numDevices]

    def run(self):  
        print("Decode started!")
        
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            #opener = "open" if sys.platform == "darwin" else ""
            subprocess.call(self.arrCall)
        #os.chdir(current_dir)
        #current_dir = os.getcwd()

        # process_string='..\\WaveDump\\compile\\bin\\x64\\Debug\\WaveDump.exe'
        # process_string = 'mkdir test'
        # subprocess.run(['mkdir test'],shell=True)
        self.finished.emit()
