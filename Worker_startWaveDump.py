from PyQt5.QtCore import *
import subprocess
import time
import sys
import os



class Worker_startWaveDump(QObject):
    finished = pyqtSignal()
    # update_log_file_name = pyqtSignal(str)

    def __init__(self):
        super(Worker_startWaveDump, self).__init__()
        filename = '../wavedump-3.10.6/src/wavedump'
        self.arrCall = [filename]

    def run(self):  
        current_dir = os.getcwd()
        # print(current_dir)
        print("WaveDump started!")
        
        #os.chdir('..\\WaveDump\\compile\\bin\\x64\\Debug')
        #os.startfile('WaveDump.exe')
        #filepath = '../WaveDump/compile/bin/x64/Debug'
        #os.chdir(filepath)
        #os.startfile('.\\WaveDump.exe')
        #print(os.listdir("."))
        #os.startfile(filepath)
        filename = '../wavedump-3.10.6/src/wavedump'

        if sys.platform == "win32":
            filepath = '../wavedump-3.10.6'
            filename = 'WaveDump.exe'
            os.chdir(os.path.normpath(filepath))
            # os.startfile(os.path.normpath(filename))
            os.startfile(filename)
            os.chdir(os.path.normpath(current_dir))
            # current_dir = os.getcwd()
            # print(current_dir)

        else:
            #opener = "open" if sys.platform == "darwin" else ""
            subprocess.call(self.arrCall)
        #os.chdir(current_dir)
        #current_dir = os.getcwd()

        # process_string='..\\WaveDump\\compile\\bin\\x64\\Debug\\WaveDump.exe'
        # process_string = 'mkdir test'
        # subprocess.run(['mkdir test'],shell=True)
        self.finished.emit()
