import socket
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import subprocess
import struct
import time
from CallProcess import *
from MonitorPlots import *



class tab_PIcontrol(QtCore.QObject):

    low_voltage_set = QtCore.pyqtSignal(float)
    high_voltage_set = QtCore.pyqtSignal(float)

    def __init__(self, run_config, run_status, MainWindow):
        super().__init__()
        self.run_config = run_config
        self.status = run_status
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)

        controlWindow = QtWidgets.QWidget()
        controlWindowLayout = QtWidgets.QHBoxLayout(controlWindow)
        sectionLayout.addWidget(controlWindow)

        self.buttonWindow = QtWidgets.QWidget()
        self.buttonWindow.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout = QtWidgets.QGridLayout(self.buttonWindow)
        controlWindowLayout.addWidget(self.buttonWindow)

        row = 0
        column = 0

        self.label = QtWidgets.QLabel()
        self.label.setText("IP address")
        self.gridLayout.addWidget(self.label, row, column, 1, 1)

        column += 1
        self.label = QtWidgets.QLabel()
        self.label.setText("Port")
        self.gridLayout.addWidget(self.label, row, column, 1, 1)

        column += 1
        self.label = QtWidgets.QLabel()
        self.label.setText("LED Low V (V)")
        self.gridLayout.addWidget(self.label, row, column, 1, 1)

        row += 1
        column = 0
        self.lineEdit_ipaddress = QtWidgets.QLineEdit()
        self.lineEdit_ipaddress.setText('172.27.137.34')
        self.gridLayout.addWidget(self.lineEdit_ipaddress,row, column, 1, 1)

        column += 1
        self.lineEdit_port = QtWidgets.QLineEdit()
        self.lineEdit_port.setText('7777')
        self.gridLayout.addWidget(self.lineEdit_port,row, column, 1, 1)

        column += 1
        self.lowVoltage_spinbox = QtWidgets.QDoubleSpinBox()
        self.lowVoltage_spinbox.setRange(0, 4.8)
        self.lowVoltage_spinbox.setSuffix(' V')
        self.gridLayout.addWidget(self.lowVoltage_spinbox, row, column, 1, 1)

        column += 1
        self.pushButton_set_LED_low_voltage = QtWidgets.QPushButton()
        self.pushButton_set_LED_low_voltage.setText("Set LED Bias")
        self.gridLayout.addWidget(self.pushButton_set_LED_low_voltage, row, column, 1, 1)
        self.pushButton_set_LED_low_voltage.clicked.connect(self.set_LED_lowvoltage_by_client)

        row += 1
        column = 2
        self.label = QtWidgets.QLabel()
        self.label.setText("LED High Voltage")
        self.gridLayout.addWidget(self.label, row, column, 1, 1)

        column += 1
        self.checkBox_LED_HV_enable = QtWidgets.QCheckBox()
        self.checkBox_LED_HV_enable.setText("enable")
        self.checkBox_LED_HV_enable.setChecked(False)
        self.checkBox_LED_HV_enable.stateChanged.connect(self.LED_HV_enable)
        self.gridLayout.addWidget(self.checkBox_LED_HV_enable, row, column, 1, 1)

        row += 1
        column = 2
        self.highVoltage_spinbox = QtWidgets.QDoubleSpinBox()
        self.highVoltage_spinbox.setRange(4.459, 59.03)
        self.highVoltage_spinbox.setSuffix(' V')
        self.highVoltage_spinbox.setEnabled(False)
        self.gridLayout.addWidget(self.highVoltage_spinbox, row, column, 1, 1)

        column += 1
        self.pushButton_set_LED_high_voltage = QtWidgets.QPushButton()
        self.pushButton_set_LED_high_voltage.setText("Set BJT Bias")
        self.gridLayout.addWidget(self.pushButton_set_LED_high_voltage, row, column, 1, 1)
        self.pushButton_set_LED_high_voltage.clicked.connect(self.set_LED_highvoltage_by_client)


        self.monitor_plots = MonitorPlots(self.status)
        self.monitor_plots.make_plot("Front SiPM Temperature vs Time", "Temperature (C)")
        self.monitor_plots.make_plot("Back SiPM Temperature vs Time", "Temperature (C)")
        self.monitor_plots.make_plot("Box Temperature vs Time", "Temperature (C)")
        self.monitor_plots.make_plot("Humidity vs Time", "Relative Humidity (%)")
        self.monitor_plots.request_monitor_data.connect(self.update_plot)
        sectionLayout.addWidget(self.monitor_plots.get_layout_widget())

        row += 1
        self.gridLayout.addWidget(self.monitor_plots.start_button, row, 0, 1, 1)
        self.gridLayout.addWidget(self.monitor_plots.stop_button, row, 1, 1, 1)

        column = 4
        row = 0
        self.monitor_front_temperature = QtWidgets.QCheckBox()
        self.monitor_front_temperature.setText("Enable Front Temperature")
        self.monitor_front_temperature.setChecked(True)
        self.gridLayout.addWidget(self.monitor_front_temperature, row, column)

        row += 1
        self.monitor_rear_temperature = QtWidgets.QCheckBox()
        self.monitor_rear_temperature.setText("Enable Rear Temperature")
        self.monitor_rear_temperature.setChecked(True)
        self.gridLayout.addWidget(self.monitor_rear_temperature, row, column)

        row += 1
        self.monitor_box_temperature = QtWidgets.QCheckBox()
        self.monitor_box_temperature.setText("Enable Box Temperature")
        self.monitor_box_temperature.setChecked(True)
        self.gridLayout.addWidget(self.monitor_box_temperature, row, column)
        
        row += 1
        self.monitor_humidity = QtWidgets.QCheckBox()
        self.monitor_humidity.setText("Enable Humidity")
        self.monitor_humidity.setChecked(True)
        self.gridLayout.addWidget(self.monitor_humidity, row, column)



        dacWindow = QtWidgets.QWidget()
        dacWindowLayout = QtWidgets.QGridLayout(dacWindow)
        controlWindowLayout.addWidget(dacWindow)

        row = 0
        column = 0
        self.dac_spinbox_list = []
        self.dac_checkbox_list = []
        for i in range(4):
            DAC_checkBox = QtWidgets.QCheckBox()
            DAC_checkBox.setText(str(i))
            dacWindowLayout.addWidget(DAC_checkBox, row, i)
            self.dac_checkbox_list.append(DAC_checkBox)

        row += 1
        for i in range(4):
            dac_spinbox = QtWidgets.QDoubleSpinBox()
            dac_spinbox.setRange(0, 2.5)
            dac_spinbox.setValue(0)
            dacWindowLayout.addWidget(dac_spinbox, row, i)
            self.dac_spinbox_list.append(dac_spinbox)

        row += 1
        for i in range(4):
            DAC_checkBox = QtWidgets.QCheckBox()
            DAC_checkBox.setText(str(4 + i))
            dacWindowLayout.addWidget(DAC_checkBox, row, i)
            self.dac_checkbox_list.append(DAC_checkBox)

        row += 1
        for i in range(4):
            dac_spinbox = QtWidgets.QDoubleSpinBox()
            dac_spinbox.setRange(0, 2.5)
            dac_spinbox.setValue(0)
            dacWindowLayout.addWidget(dac_spinbox, row, i)
            self.dac_spinbox_list.append(dac_spinbox)

        for i in range(8):
            self.dac_checkbox_list[i].stateChanged.connect(self.DAC_enable)
            self.dac_spinbox_list[i].setEnabled(False)
            self.dac_checkbox_list[i].setChecked(False)

        column = 4
        self.pushButton_set_DAC = QtWidgets.QPushButton()
        self.pushButton_set_DAC.setText("Set SiPM DAC voltage")
        dacWindowLayout.addWidget(self.pushButton_set_DAC, row, column)
        self.pushButton_set_DAC.clicked.connect(self.set_DAC_voltage)
 
    def DAC_enable(self):
        for i in range(8):
            if self.checkBox_SiPM_DAC_list[i].isChecked():
                self.lineEdit_SiPM_DAC_list[i].setEnabled(True)
            else:
                self.lineEdit_SiPM_DAC_list[i].setEnabled(False)

    def set_DAC_voltage(self):
        for i in range(8):
            if self.checkBox_SiPM_DAC_list[i].isChecked():
                self.callclient('SipmDacWrite WriteUpdate {} {}'.format(i, self.lineEdit_SiPM_DAC_list[i].text()))
            else:
                self.callclient('SipmDacControl PowerDown {} 0'.format(i))

    def LED_HV_enable(self):
        self.highVoltage_spinbox.setEnabled(self.checkBox_LED_HV_enable.isChecked())
        if self.checkBox_LED_HV_enable.isChecked():
            self.callclient('VoltageControl HighVoltageEnable true')
        else:
            self.callclient('VoltageControl HighVoltageEnable false')


    def set_LED_lowvoltage_by_client(self):
        voltage = self.lowVoltage_spinbox.value()
        if self.callclient("VoltageControl LowVoltageSet {}".format(voltage * 1000)):
            self.low_voltage_set.emit(voltage)

    def set_LED_highvoltage_by_client(self):
        voltage = float(self.lineEdit_high_voltage.text())
        if self.callclient("VoltageControl HighVoltageSet {}".format(voltage * 1000)):
            self.high_voltage_set.emit(voltage)

    def read_client_float(self, cmd_args):
        x = ClientReadProcess.execute(self.lineEdit_ipaddress.text(), self.lineEdit_port.text(), cmd_args)
        try:
            return float(x)
        except Exception as e:
            return None

    def callclient(self,cmd_args):
        return ClientVerboseProcess.execute(self.lineEdit_ipaddress.text(), self.lineEdit_port.text(), cmd_args)

    def update_plot(self):
        # request humidity control to start a read; will actually read out later
        if self.monitor_humidity.isChecked() or self.monitor_box_temperature.isChecked():
            self.read_client_float('HumidityControl RequestRead')
            QtCore.QThread.currentThread().msleep(75)


        if self.monitor_front_temperature.isChecked():
            y = self.read_client_float('TemperatureRead Read 0')
            if y != None:
                self.monitor_plots.add_point(0, y)

        if self.monitor_rear_temperature.isChecked():
            y = self.read_client_float('TemperatureRead Read 1')
            if y != None:
                self.monitor_plots.add_point(1, y)

        if self.monitor_box_temperature.isChecked():
            y = self.read_client_float('HumidityControl ReadTemperature')
            if y != None:
                self.monitor_plots.add_point(2, y)

        if self.monitor_humidity.isChecked():
            y = self.read_client_float('HumidityControl ReadHumidity')
            if y != None:
                self.monitor_plots.add_point(3, y)

    def power_down(self):
        self.callclient('VoltageControl LowVoltageSet 0')
        self.callclient('VoltageControl HighVoltageEnable false')
