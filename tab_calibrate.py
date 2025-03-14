from PyQt5 import QtCore, QtGui, QtWidgets
from CallProcess import *
from Worker_startDAQ import *
import pyvisa
import time
from GUI_lowlevel import *


class CalibrateProcess(CallProcess):
    def __init__(self):
        self.visa_resources=0
        self.siggen_inst = 0
        self.ps_inst = 0

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
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)
        buttonWindow = QtWidgets.QWidget()
        buttonWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout = QtWidgets.QGridLayout(buttonWindow)



        row = 0
        column = 0
        self.pushButton_calibrateDRS = create_button("Calibrate DRS's", row, column, 1, self.calibrate_DRS, layout=self.gridLayout)

        column += 1
        self.pushButton_resetDRS = create_button("Reset DRS's", row, column, 1, Reset_DAQ.execute, layout=self.gridLayout)

        row += 1
        column = 0
        self.pushButton_open_SigGen = create_button("Find SigGen", row, column, 1, self.open_SigGen, layout=self.gridLayout)

        column += 1
        self.pushButton_set_SigGen = create_button("Set SigGen", row, column, 1, self.setup_SigGen, layout=self.gridLayout)

        column += 1
        self.pushButton_en_SigGen = create_checkbox("Output En", row, column, 1, self.output_enable, layout=self.gridLayout)


        row += 1
        column = 0
        self.spinBox_freq=create_spinbox("Frequency(Hz)", row, column, 1, initvalue=1000, layout=self.gridLayout)

        column += 2
        self.lineEdit_width=create_lineedit("Pulse Width(s)", row, column, 1, initvalue='1E-6', layout=self.gridLayout)
        
        column += 2
        self.lineEdit_delay=create_lineedit("CH2 Delay Width(s)", row, column, 1, initvalue='75E-9', layout=self.gridLayout)
        
        row += 1
        column = 0
        self.spinBox_CH1_high=create_double_spinbox("CH1 high(V)", row, column, 1, initvalue=1.0, layout=self.gridLayout)
        
        column += 2
        self.spinBox_CH1_low=create_double_spinbox("CH1 low(V)", row, column, 1, initvalue=0, layout=self.gridLayout)
        
        column += 2
        self.spinBox_CH2_high=create_double_spinbox("CH2 high(V)", row, column, 1, initvalue=1.0, layout=self.gridLayout)
        

        column += 2
        self.spinBox_CH2_low=create_double_spinbox("CH2 low(V)", row, column, 1, initvalue=0, layout=self.gridLayout)
        
        row += 1
        column = 0
        self.pushButton_open_ps = create_button("Find Power supply", row, column, 1, self.open_powersupply, layout=self.gridLayout)

        column += 1
        self.pushButton_set_ps = create_button("Set voltage", row, column, 1, self.setup_power_supply, layout=self.gridLayout)

        column += 1
        self.spinBox_ps_vol=create_double_spinbox("Voltage(V)", row, column, 1, initvalue=0, layout=self.gridLayout)
        

     
        sectionLayout.addWidget(buttonWindow)

    def calibrate_DRS(self):
        CalibrateProcess.execute()

    def open_SigGen(self):  
        # Initialize VISA resource manager

        self.visa_resources = pyvisa.ResourceManager("@py")  #pyvisa-py works, pyvisa-ni does not
        # List available devices
        resources = self.visa_resources.list_resources()
        print("Available resources:", resources)

        # Connect to AFG3252 (Modify the resource string if needed)
        self.siggen_inst = self.visa_resources.open_resource('USB0::1689::837::C021122::0::INSTR')
        reply = self.siggen_inst.query('*IDN?')
        if(len(reply)):
            print("Signal generator device found: "+reply)
        else:
            print("Signal generator device not found.")

    def open_powersupply(self):  
        # Initialize VISA resource manager

        self.visa_resources = pyvisa.ResourceManager("@py")  #pyvisa-py works, pyvisa-ni does not
        # List available devices
        resources = self.visa_resources.list_resources()
        print("Available resources:", resources)

        # Connect to AFG3252 (Modify the resource string if needed)
        self.ps_inst = self.visa_resources.open_resource('ASRL/dev/ttyACM0::INSTR')
        reply = self.ps_inst.query('*IDN?')
        if(len(reply)):
            print("Power supply device found: "+reply)
        else:
            print("Power supply device not found.")

    def setup_SigGen(self):
        # Configure CH1 and CH2 for pulse wave
        if self.siggen_inst:
            for ch in [1, 2]:
                self.siggen_inst.write(f"SOURCE{ch}:FUNCTION PULSE")       # Set function to pulse
                time.sleep(0.1)                              # between commands for stability.
                self.siggen_inst.write(f"SOURCE{ch}:FREQUENCY {self.spinBox_freq.value()}")      # Set frequency to 1 kHz
                time.sleep(0.1)
                
                self.siggen_inst.write(f"SOURCE{ch}:PULSE:WIDTH {self.lineEdit_width.text()}")   # Set pulse width to 1000 ns (1µs)
                time.sleep(0.1)

            self.siggen_inst.write(f"SOURCE1:VOLTAGE:HIGH {self.spinBox_CH1_high}")      # Set high voltage to 1V
            time.sleep(0.1)
            self.siggen_inst.write(f"SOURCE1:VOLTAGE:LOW {self.spinBox_CH1_low}")       # Set low voltage to 0V
            time.sleep(0.1)
            self.siggen_inst.write(f"SOURCE2:VOLTAGE:HIGH {self.spinBox_CH2_high}")      # Set high voltage to 1V
            time.sleep(0.1)
            self.siggen_inst.write(f"SOURCE2:VOLTAGE:LOW {self.spinBox_CH2_low}")       # Set low voltage to 0V
            time.sleep(0.1)

            # Synchronize both channels
            self.siggen_inst.write("SOURCE2:FREQ:COUPLE ON")  # CH2 will follow CH1, does not work
            time.sleep(0.1)
            self.siggen_inst.write("SOURCE1:PULSE:DELAY 0")
            time.sleep(0.1)
            self.siggen_inst.write("SOURCE2:PHASE:SYNC") # Ensure phase synchronization, does not work either
            time.sleep(0.1)
            self.siggen_inst.write(f"SOURCE2:PULSE:DELAY {self.lineEdit_delay.text()}")
            print("Signal generator set up completes")
        else:
            print("Please open signal generator inst first.")

    def output_enable(self, state):

        value = 1 if state == Qt.Checked else 0
        if self.siggen_inst:
            if value:
                # Enable both channels
                self.siggen_inst.write("OUTPUT1 ON")
                time.sleep(0.1)
                self.siggen_inst.write("OUTPUT2 ON")
                time.sleep(0.1)
                print("Signal generator output enabled for both channels")
            else:
                self.siggen_inst.write("OUTPUT1 OFF")
                time.sleep(0.1)
                self.siggen_inst.write("OUTPUT2 OFF")
                time.sleep(0.1)
                print("Signal generator output disabled for both channels")
        else:
            print("Please open signal generator inst first.")

    def setup_power_supply(self):
        if self.ps_inst:
            self.ps_inst.write(f"VSET1:{self.spinBox_ps_vol.value()}")
            time.sleep(0.1)
            print(f"Power supply output set to {self.spinBox_ps_vol.value()} V")
        else:
            print("Please open power supply inst first.")




