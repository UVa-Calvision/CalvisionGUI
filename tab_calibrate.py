from PyQt5 import QtCore, QtGui, QtWidgets
from CallProcess import *
from Worker_startDAQ import *


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
        sectionLayout = QtWidgets.QHBoxLayout(MainWindow)

        calibrateWindow = QtWidgets.QWidget()
        calibrateLayout = QtWidgets.QFormLayout(calibrateWindow)
        sectionLayout.addWidget(calibrateWindow)

        calibrateLabel = QtWidgets.QLabel()
        calibrateLabel.setText("Calibration")
        calibrateLayout.addRow(calibrateLabel)
        calibrateLayout.setAlignment(calibrateLabel, QtCore.Qt.AlignHCenter)

        pushButton_calibrateDRS = QtWidgets.QPushButton()
        pushButton_calibrateDRS.setText("Calibrate DRS's")
        calibrateLayout.addRow(pushButton_calibrateDRS)
        pushButton_calibrateDRS.clicked.connect(self.calibrate_DRS)

        pushButton_resetDRS = QtWidgets.QPushButton()
        pushButton_resetDRS.setText("Reset DRS's")
        pushButton_resetDRS.clicked.connect(Reset_DAQ.execute)
        calibrateLayout.addWidget(pushButton_resetDRS)

        self.calibrateOffset_button = QtWidgets.QPushButton()
        self.calibrateOffset_button.setText("Calibrate DRS channel offsets")
        calibrateLayout.addWidget(self.calibrateOffset_button)

        pulserWindow = QtWidgets.QWidget()
        pulserLayout = QtWidgets.QFormLayout(pulserWindow)
        sectionLayout.addWidget(pulserWindow)

        pulserLabel = QtWidgets.QLabel()
        pulserLabel.setText("Pulser")
        pulserLayout.addRow(pulserLabel)
        pulserLayout.setAlignment(pulserLabel, QtCore.Qt.AlignHCenter)

        self.pushButton_pulseOn = QtWidgets.QPushButton()
        self.pushButton_pulseOn.setText("Pulser On")
        pulserLayout.addWidget(self.pushButton_pulseOn)
        self.pushButton_pulseOn.clicked.connect(self.pulse_on)
        self.pushButton_pulseOn.setEnabled(True)

        self.pushButton_pulseOff = QtWidgets.QPushButton()
        self.pushButton_pulseOff.setText("Pulser Off")
        pulserLayout.addWidget(self.pushButton_pulseOff)
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

    def power_down(self):
        self.pulse_off()
