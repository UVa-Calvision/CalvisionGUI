from PyQt5 import QtCore, QtGui, QtWidgets
from CallProcess import *


class PulserProcess(CallProcess):
    def __init__(self):
        pass

    def handle_output(self, line):
        print(line)

    def execute(on):
        postfix = "on"
        if not on:
            postfix = "off"
        PulserProcess().run("python3 /home/uva/local_install/python/pulse{}.py".format(postfix))

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
        self.pushButton_pulseOn = QtWidgets.QPushButton()
        self.pushButton_pulseOn.setText("Pulser On")
        self.sectionLayout.addWidget(self.pushButton_pulseOn, row, column, 1, 1)
        self.pushButton_pulseOn.clicked.connect(self.pulse_on)
        self.pushButton_pulseOn.setEnabled(True)

        column += 1
        self.pushButton_pulseOff = QtWidgets.QPushButton()
        self.pushButton_pulseOff.setText("Pulser Off")
        self.sectionLayout.addWidget(self.pushButton_pulseOff, row, column, 1, 1)
        self.pushButton_pulseOff.clicked.connect(self.pulse_off)
        self.pushButton_pulseOff.setEnabled(True)


    def calibrate_DRS(self):
        CalibrateProcess.execute()

    def pulse_on(self):
        PulserProcess.execute(True)
        self.pulser_enabled.emit(True)

    def pulse_off(self):
        PulserProcess.execute(False)
        self.pulser_enabled.emit(False)
