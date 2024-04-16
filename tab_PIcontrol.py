import socket
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import subprocess
import struct
import time
from CallProcess import *



class tab_PIcontrol(object):

    def __init__(self, MainWindow):
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)

        controlWindow = QtWidgets.QWidget()
        controlWindowLayout = QtWidgets.QHBoxLayout(controlWindow)
        sectionLayout.addWidget(controlWindow)

        self.buttonWindow = QtWidgets.QWidget()
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
        self.label.setText("LED Low V (mV)")
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
        self.lineEdit_low_voltage = QtWidgets.QLineEdit()
        self.lineEdit_low_voltage.setText('0')
        self.gridLayout.addWidget(self.lineEdit_low_voltage,row, column, 1, 1)

        column += 1
        self.pushButton_set_LED_low_voltage = QtWidgets.QPushButton()
        self.pushButton_set_LED_low_voltage.setText("Set LED Bias")
        self.gridLayout.addWidget(self.pushButton_set_LED_low_voltage, row, column, 1, 1)
        self.pushButton_set_LED_low_voltage.clicked.connect(self.set_LED_lowvoltage_by_client)

        # column += 1
        # self.pushButton_TCPsend = QtWidgets.QPushButton()
        # self.pushButton_TCPsend.setText("TCP Send")
        # self.gridLayout.addWidget(self.pushButton_TCPsend, row, column, 1, 1)
        # self.pushButton_TCPsend.clicked.connect(self.TCPsend)
        row += 1
        column = 2
        self.label = QtWidgets.QLabel()
        self.label.setText("LED High V (mV)")
        self.gridLayout.addWidget(self.label, row, column, 1, 1)

        column += 1
        self.checkBox_LED_HV_enable = QtWidgets.QCheckBox()
        self.checkBox_LED_HV_enable.stateChanged.connect(self.LED_HV_enable)
        self.checkBox_LED_HV_enable.setText("enable")
        self.checkBox_LED_HV_enable.setChecked(True)
        self.gridLayout.addWidget(self.checkBox_LED_HV_enable, row, column, 1, 1)

        row += 1
        column = 2
        self.lineEdit_high_voltage = QtWidgets.QLineEdit()
        self.lineEdit_high_voltage.setText('0')
        self.gridLayout.addWidget(self.lineEdit_high_voltage, row, column, 1, 1)

        column += 1
        self.pushButton_set_LED_high_voltage = QtWidgets.QPushButton()
        self.pushButton_set_LED_high_voltage.setText("Set BJT Bias")
        self.gridLayout.addWidget(self.pushButton_set_LED_high_voltage, row, column, 1, 1)
        self.pushButton_set_LED_high_voltage.clicked.connect(self.set_LED_highvoltage_by_client)

        row += 1
        column = 0
        self.pushButton_timer_start = QtWidgets.QPushButton()
        self.pushButton_timer_start.setText("Start Monitor")
        self.gridLayout.addWidget(self.pushButton_timer_start, row, column, 1, 1)
        self.pushButton_timer_start.clicked.connect(self.timer_start)
        self.pushButton_timer_start.setEnabled(True)

        column += 1
        self.pushButton_timer_stop = QtWidgets.QPushButton()
        self.pushButton_timer_stop.setText("Stop")
        self.gridLayout.addWidget(self.pushButton_timer_stop, row, column, 1, 1)
        self.pushButton_timer_stop.clicked.connect(self.timer_stop)
        self.pushButton_timer_stop.setEnabled(False)



        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)

        self.time1 = [0]
        self.temp1 = [0]

        self.time2 = [0]
        self.temp2 = [0]

        self.time3 = [0]
        self.temp3 = [0]

        self.time4 = [0]
        self.humidity = [0]

        # GraphicsLayoutWidget
        temperature_gridLayout = pg.GraphicsLayoutWidget()
        temperature_gridLayout.setBackground('w')
        self_line_temp1 = self.plot_data(layoutWidget = temperature_gridLayout, title = "Front SiPM Temperature vs Time", ylabel = "Temperature (C)")
        self_line_temp2 = self.plot_data(layoutWidget = temperature_gridLayout, title = "Back SiPM Temperature vs Time", ylabel = "Temperature (C)")
        self_line_temp3 = self.plot_data(layoutWidget = temperature_gridLayout, title = "Humidity Control Temperature vs Time", ylabel = "Temperature (C)")
        self_line_humidity = self.plot_data(layoutWidget = temperature_gridLayout, title = "Humidity vs Time", ylabel = "Relative Humidity (%)")
        sectionLayout.addWidget(temperature_gridLayout)


        dacWindow = QtWidgets.QWidget()
        dacWindowLayout = QtWidgets.QGridLayout(dacWindow)
        controlWindowLayout.addWidget(dacWindow)

        row = 0
        column = 0
        self.lineEdit_SiPM_DAC_list=[]
        self.checkBox_SiPM_DAC_list=[]
        for i in range(4):
            DAC_checkBox = QtWidgets.QCheckBox()
            DAC_checkBox.setText(str(i))
            dacWindowLayout.addWidget(DAC_checkBox, row, i, 1, 1)
            self.checkBox_SiPM_DAC_list.append(DAC_checkBox)

        row += 1
        for i in range(4):
            lineEdit_DAC = QtWidgets.QLineEdit()
            lineEdit_DAC.setText('0.0')
            dacWindowLayout.addWidget(lineEdit_DAC,row, i, 1, 1)
            self.lineEdit_SiPM_DAC_list.append(lineEdit_DAC)

        row += 1
        for i in range(4):
            DAC_checkBox = QtWidgets.QCheckBox()
            DAC_checkBox.setText(str(i+4))
            dacWindowLayout.addWidget(DAC_checkBox, row, i, 1, 1)
            self.checkBox_SiPM_DAC_list.append(DAC_checkBox)

        row += 1
        for i in range(4):
            lineEdit_DAC = QtWidgets.QLineEdit()
            lineEdit_DAC.setText('0.0')
            dacWindowLayout.addWidget(lineEdit_DAC,row, i, 1, 1)
            self.lineEdit_SiPM_DAC_list.append(lineEdit_DAC)

        for i in range(8):
            self.checkBox_SiPM_DAC_list[i].stateChanged.connect(self.DAC_enable)
            self.lineEdit_SiPM_DAC_list[i].setEnabled(False)
            self.checkBox_SiPM_DAC_list[i].setChecked(False)

        column = 4
        self.pushButton_set_DAC = QtWidgets.QPushButton()
        self.pushButton_set_DAC.setText("Set SiPM DAC vol")
        dacWindowLayout.addWidget(self.pushButton_set_DAC, row, column, 1, 1)
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
        if self.checkBox_LED_HV_enable.isChecked():
            self.callclient('VoltageControl HighVoltageEnable true')
        else:
            self.callclient('VoltageControl HighVoltageEnable false')


    def set_LED_lowvoltage_by_client(self):
        self.callclient("VoltageControl LowVoltageSet " + self.lineEdit_low_voltage.text())

    def set_LED_highvoltage_by_client(self):
        self.callclient("VoltageControl HighVoltageSet " + self.lineEdit_high_voltage.text())

    def read_client_float(self, cmd_args):
        x = ClientReadProcess().run(self.lineEdit_ipaddress.text(), self.lineEdit_port.text(), cmd_args)
        try:
            return float(x)
        except Exception as e:
            return None

    def callclient(self,cmd_args):
        ClientVerboseProcess().run(self.lineEdit_ipaddress.text(), self.lineEdit_port.text(), cmd_args)

    def timer_start(self):
        self.timer.start()
        self.pushButton_timer_start.setEnabled(False)
        self.pushButton_timer_stop.setEnabled(True)
        self.monitor_time = 0

    def timer_stop(self):
        self.timer.stop()
        self.pushButton_timer_start.setEnabled(True)
        self.pushButton_timer_stop.setEnabled(False)

    def plot_data(self, layoutWidget, title, ylabel):
        pen = pg.mkPen(color='b', width=3)
        styles = {"color": "red", "font-size": "12px"}
    
        plot = layoutWidget.addPlot()
        plot.setTitle(title, color = 'b', size = '10pt')
        plot.setLabel("left", ylabel, **styles)
        plot.setLabel("bottom", "Time (sec)", **styles)
        plot.addLegend()
        plot.showGrid(x = True, y = True)
        return plot.plot([0], [0], pen = pen)


    def update_plot(self):
        self.monitor_time += self.timer.interval() / 1000

        # request humidity control to start a read; will actually read out later
        self.read_client_float('HumidityControl RequestRead')

        y = self.read_client_float('TemperatureRead Read 0')
        if y != None:
            self.time1.append(self.monitor_time)
            self.temp1.append(y)
            self.line_temp1.setData(self.time1, self.temp1)

        y = self.read_client_float('TemperatureRead Read 1')
        if y != None:
            self.time2.append(self.monitor_time)
            self.temp2.append(y)
            self.line_temp2.setData(self.time2, self.temp2)

        y = self.read_client_float('HumidityControl ReadTemperature')
        if y != None:
            self.time3.append(self.monitor_time)
            self.temp3.append(y)
            self.line_temp3.setData(self.time3, self.temp3)

        y = self.read_client_float('HumidityControl ReadHumidity')
        if y != None:
            self.time4.append(self.monitor_time)
            self.humidity.append(y)
            # self.line_humidity.setData(self.time4, self.humidity)
        




