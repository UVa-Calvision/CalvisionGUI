from PyQt5 import QtCore, QtGui, QtWidgets
from RunConfig import *
import time
import serial
import os

class tab_rotor_control(QtCore.QObject):

    angle_changed = QtCore.pyqtSignal(int)

    min_angle = -90
    max_angle = 90

    def __init__(self, run_config, status, devices, MainWindow):
        super().__init__()
        self.run_config = run_config
        self.status = status
        self.devices = devices

        self.serial_port = None
        self.angle = None
        self.angle_file = "rotor_angle.txt"

        if os.path.exists(self.angle_file):
            with open(self.angle_file, 'r') as infile:
                try:
                    angle = int(infile.readline())
                    if angle < tab_rotor_control.min_angle or angle > tab_rotor_control.max_angle:
                        print("angle {} from file outside bounds".format(angle))
                    else:
                        self.angle = angle
                except ValueError:
                    print("Couldn't read angle from file")
        else:
            print("No existing angle file...")

        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)

        controlWindow = QtWidgets.QWidget()
        controlWindow.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        controlLayout = QtWidgets.QFormLayout(controlWindow)
        sectionLayout.addWidget(controlWindow)


        self.rotorPort_comboBox = QtWidgets.QComboBox()
        self.rotorPort_comboBox.addItems(self.devices.rotor_devices)
        controlLayout.addRow("Rotor Device", self.rotorPort_comboBox)

        
        self.rotorEnable_checkBox = QtWidgets.QCheckBox()
        self.rotorEnable_checkBox.setEnabled(len(self.devices.rotor_devices) > 0)
        self.rotorEnable_checkBox.toggled.connect(self.setup_device)
        controlLayout.addRow("Enable Rotor Control", self.rotorEnable_checkBox)

        self.angle_comboBox = QtWidgets.QComboBox()
        self.angle_comboBox.addItems(config_options['Angle'])
        self.angle_comboBox.setEditable(True)
        self.angle_comboBox.setEnabled(False)
        controlLayout.addRow("Angle", self.angle_comboBox)

        self.updateAngle_button = QtWidgets.QPushButton()
        self.updateAngle_button.setText("Update Angle")
        self.updateAngle_button.setEnabled(False)
        self.updateAngle_button.clicked.connect(self.update_angle)
        controlLayout.addRow(self.updateAngle_button)


    def setup_device(self):
        if (self.rotorEnable_checkBox.isChecked()):
            port = self.rotorPort_comboBox.currentText()
            if len(port):
                self.serial_port = serial.Serial(
                                port,
                                baudrate=9600,
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                timeout=0.1)
                print("Opening port: "+str(self.serial_port))
                self.angle_comboBox.setEnabled(True)
                self.updateAngle_button.setEnabled(True)
            else:
                print("No USB devices found.")
                self.angle_comboBox.setEnabled(False)
                self.updateAngle_button.setEnabled(False)
        else:
            print("Closing port")
            self.serial_port.close()
            print(self.serial_port)
            self.serial_port = 0
            self.angle_comboBox.setEnabled(False)
            self.updateAngle_button.setEnabled(False)

    def update_angle(self):
        if self.serial_port == None:
            print("Cannot set rotor angle since no device is setup")
            return

        try:
            new_angle = int(self.angle_comboBox.currentText())
            if new_angle < tab_rotor_control.min_angle:
                print("Cannot set angle {} below {}".format(new_angle, tab_rotor_control.min_angle))
                return
            elif new_angle > tab_rotor_control.max_angle:
                print("Cannot set angle {} above {}".format(new_angle, tab_rotor_control.max_angle))
                return
            elif new_angle == self.angle:
                print("New angle {} same as current angle {}".format(new_angle, self.angle))
                return

            # Assume at 0 angle on startup- bad
            if self.angle == None:
                self.angle = 0

            change = new_angle - self.angle
            change_dir = 1 if change < 0 else 0
            change_mag = abs(change)
            command = '<{},{},0>'.format(change_dir, change_mag)

            print("Current Angle = {}".format(self.angle))
            print("New Angle = {}".format(new_angle))
            print("Angle Change = {}".format(change))
            print("Sending command = {}".format(command))

            self.serial_port.write(bytearray(command,'ascii'))
            self.serial_port.flush()

            time.sleep(0.05)

            result = self.serial_port.readline()
            while len(result) > 0:
                print("UART read back: {}".format(result.decode('ascii')))
                result = self.serial_port.readline()

            self.angle = new_angle
            try:
                with open(self.angle_file, 'w') as outfile:
                    outfile.write('{}'.format(self.angle))
            except Exception:
                print("[ERROR] FAILED TO WRITE CURRENT ANGLE TO FILE!")

            self.angle_changed.emit(self.angle)

        except ValueError:
            print("Cannot convert {} to an integer in degrees".format(self.angle_comboBox.currentText()))

