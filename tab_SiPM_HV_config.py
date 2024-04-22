from PyQt5 import QtCore, QtGui, QtWidgets
from a7585d import A7585D 
from a7585d import A7585D_REG
import time

import pyqtgraph as pg
from random import randint
from MonitorPlots import *


class sipm_config:
    def __init__(self, devices, gridLayout, row):

        self.hv = A7585D()

        self.name = ''
        self.device_file = ''
        self.log_file = ''
        if row == 1:
            self.name = 'Front'
            self.device_file = '/dev/CAEN_Front_Bias_21756'
            self.log_file = 'hv_front_log.csv'
        elif row == 2:
            self.name = 'Rear'
            self.device_file = '/dev/CAEN_Rear_Bias_21758'
            self.log_file = 'hv_rear_log.csv'

        column = 0
        label = QtWidgets.QLabel()
        label.setText(self.name)
        gridLayout.addWidget(label, row, column)

        column += 1
        self.comboBox_port = QtWidgets.QComboBox()
        self.comboBox_port.addItems(devices)
        if self.device_file in devices:
            self.comboBox_port.setCurrentIndex(devices.index(self.device_file))
        else:
            print("Didn't find default {} SiPM {}".format(self.name, self.device_file))
        gridLayout.addWidget(self.comboBox_port, row, column)

        column += 1
        openDevice_button = QtWidgets.QPushButton()
        openDevice_button.setText("Open Device")
        openDevice_button.clicked.connect(self.open_device)
        gridLayout.addWidget(openDevice_button, row, column)

        column += 1
        self.maxV_spinbox = QtWidgets.QDoubleSpinBox()
        self.maxV_spinbox.setRange(20, 85)
        self.maxV_spinbox.setValue(50)
        self.maxV_spinbox.setSuffix(' V')
        self.maxV_spinbox.setEnabled(False)
        gridLayout.addWidget(self.maxV_spinbox, row, column)

        column += 1
        self.maxI_spinbox = QtWidgets.QDoubleSpinBox()
        self.maxI_spinbox.setRange(0, 1)
        self.maxI_spinbox.setValue(0.5)
        self.maxI_spinbox.setSuffix(' mA')
        self.maxI_spinbox.setEnabled(False)
        gridLayout.addWidget(self.maxI_spinbox, row, column)

        column += 1
        self.ramp_spinbox = QtWidgets.QDoubleSpinBox()
        self.ramp_spinbox.setRange(0, 5)
        self.ramp_spinbox.setValue(2)
        self.ramp_spinbox.setSuffix(' V/s')
        self.ramp_spinbox.setEnabled(False)
        gridLayout.addWidget(self.ramp_spinbox, row, column)

        column += 1
        self.targetV_spinbox = QtWidgets.QDoubleSpinBox()
        self.targetV_spinbox.setRange(20, 85)
        self.targetV_spinbox.setValue(20)
        self.targetV_spinbox.setSuffix(' V')
        self.targetV_spinbox.setEnabled(False)
        gridLayout.addWidget(self.targetV_spinbox, row, column)

        column += 1
        self.enable_checkbox = QtWidgets.QCheckBox()
        self.enable_checkbox.setChecked(False)
        self.enable_checkbox.setEnabled(False)
        gridLayout.addWidget(self.enable_checkbox, row, column)

        column += 1
        self.apply_button = QtWidgets.QPushButton()
        self.apply_button.setText("Apply")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply)
        gridLayout.addWidget(self.apply_button, row, column)

    def open_device(self):
        try:
            self.hv.open(self.comboBox_port.currentText())
            code = self.hv.get_parameter(A7585D_REG.PRODUCT_CODE)
            if code == 54:
                print("Device opened")
                print(self.hv)
                print("Product code = {}".format(self.hv.get_parameter(A7585D_REG.PRODUCT_CODE)))
                print("Firmware ver = {}".format(self.hv.get_parameter(A7585D_REG.FW_VERSION)))
                print("Hardware ver = {}".format(self.hv.get_parameter(A7585D_REG.HW_VERSION)))
                print("Serial number = {}".format(self.hv.get_parameter(A7585D_REG.SERIAL_NUMBER)))

                self.maxV_spinbox.setEnabled(True)
                self.maxI_spinbox.setEnabled(True)
                self.ramp_spinbox.setEnabled(True)
                self.targetV_spinbox.setEnabled(True)
                self.enable_checkbox.setEnabled(True)
                self.apply_button.setEnabled(True)

                self.hv.set_parameter(A7585D_REG.CNTRL_MODE, 0)  
                self.hv.set_parameter(A7585D_REG.T_COEF_SIPM, -35)
            else:
                print("Product code does not match. Try another device.")
        except Exception as e:
            print("Failed to open device: {}".format(e))

    def apply(self):
        if self.is_open():
            self.hv.set_parameter(A7585D_REG.MAX_V, self.maxV_spinbox.value())
            self.hv.set_parameter(A7585D_REG.MAX_I, self.maxI_spinbox.value())
            self.hv.set_parameter(A7585D_REG.RAMP, self.ramp_spinbox.value())
            self.hv.set_parameter(A7585D_REG.V_TARGET, self.targetV_spinbox.value())
            if self.enable_checkbox.isChecked():
                self.hv.set_parameter(A7585D_REG.HV_ENABLE, 1)
            else:
                self.hv.set_parameter(A7585D_REG.HV_ENABLE, 0)

    def get_voltage(self):
        if self.is_open():
            return self.hv.get_parameter(A7585D_REG.MON_VOUT)
        else:
            print("Error: please check SiPM HV connection")
            return None

    def get_current(self):   
        if self.is_open():
            return self.hv.get_parameter(A7585D_REG.MON_IOUT)
        else:
            print("Error: please check SiPM HV connection")
            return None

    def power_down(self):
        if self.is_open():
            self.hv.set_parameter(A7585D_REG.V_TARGET, 20.0)
            self.hv.set_parameter(A7585D_REG.HV_ENABLE, 0)

    def is_open(self):
        return self.hv.ser != None




class tab_SiPM_HV_config(object):

    def __init__(self, run_config, status, MainWindow, devices):
        self.run_config = run_config
        self.status = status
        self.portsList = devices.caen_hv_devices
        print("Ports: {}".format(self.portsList))
        self.setup_UI(MainWindow)


    def setup_UI(self, MainWindow):

        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)
        
        buttonWindow = QtWidgets.QWidget()
        buttonWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout = QtWidgets.QGridLayout(buttonWindow)

        row = 0
        column = 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Port")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)


        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Open")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)


        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Max V")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Max I")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Ramp")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Out Voltage")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Out Enable")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Apply")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        row += 1
        self.hv_front = sipm_config(self.portsList, self.gridLayout, row)
        row += 1
        self.hv_rear = sipm_config(self.portsList, self.gridLayout, row)

        sectionLayout.addWidget(buttonWindow)


        # Add a timer to simulate new temperature measurements

        self.monitor_plots = MonitorPlots(self.status)
        self.monitor_plots.make_plot("HV Front Voltage vs Time", "Voltage (V)")
        self.monitor_plots.make_plot("HV Front Current vs Time", "Current (mA)", use_log = True)
        self.monitor_plots.make_plot("HV Rear Voltage vs Time", "Voltage (V)")
        self.monitor_plots.make_plot("HV Rear Current vs Time", "Current (mA)", use_log = True)
        self.monitor_plots.request_monitor_data.connect(self.update_plot)
        sectionLayout.addWidget(self.monitor_plots.get_layout_widget())

        row += 1
        self.gridLayout.addWidget(self.monitor_plots.start_button, row, 0, 1, 1)
        self.gridLayout.addWidget(self.monitor_plots.stop_button, row, 1, 1, 1)



    def update_plot(self):
        if self.hv_front.is_open():
            volt = self.hv_front.get_voltage()
            curr = self.hv_front.get_current()
            self.monitor_plots.add_point(0, volt)
            self.monitor_plots.add_point(1, curr)
            with open(self.hv_front.log_file, 'a') as f:
                f.write('{},{:.3f},{:.3f}\n'.format(self.status.monitor_time, volt, curr))

        if self.hv_rear.is_open():
            volt = self.hv_rear.get_voltage()
            curr = self.hv_rear.get_current()
            self.monitor_plots.add_point(2, volt)
            self.monitor_plots.add_point(3, curr)
            with open(self.hv_rear.log_file, 'a') as f:
                f.write('{},{:.3f},{:.3f}\n'.format(self.status.monitor_time, volt, curr))

    def power_down(self):
        self.hv_front.power_down()
        self.hv_rear.power_down()
