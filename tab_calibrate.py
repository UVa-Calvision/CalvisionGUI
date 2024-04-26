from PyQt5 import QtCore, QtGui, QtWidgets
from CallProcess import *
from Worker_startDAQ import *


class CalibrateProcess(CallProcess):
    def __init__(self):
        pass

    def handle_output(self, line):
        print(line)

    def execute():
        source_conda = "source /home/uva/miniforge3/etc/profile.d/conda.sh; conda activate calvision;"
        CalibrateProcess().run(source_conda + "/home/uva/local_install/bin/calibrate")


class tab_calibrate(QtCore.QObject):

    pulser_enabled = QtCore.pyqtSignal(bool)
    
    def __init__(self, MainWindow):
        super().__init__()
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        self.sectionLayout = QtWidgets.QGridLayout(MainWindow)

        row = 0
        column = 0
        self.pushButton_calibrateDRS = QtWidgets.QPushButton()
        self.pushButton_calibrateDRS.setText("Calibrate DRS's")
        self.sectionLayout.addWidget(self.pushButton_calibrateDRS, row, column, 1, 1)
        self.pushButton_calibrateDRS.clicked.connect(self.calibrate_DRS)

        column += 1
        self.pushButton_resetDRS = QtWidgets.QPushButton()
        self.pushButton_resetDRS.setText("Reset DRS's")
        self.pushButton_resetDRS.clicked.connect(Reset_DAQ.execute)
        self.sectionLayout.addWidget(self.pushButton_resetDRS, row, column, 1, 1)

    def calibrate_DRS(self):
        CalibrateProcess.execute()
