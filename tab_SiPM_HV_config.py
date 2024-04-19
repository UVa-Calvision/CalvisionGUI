from PyQt5 import QtCore, QtGui, QtWidgets
from a7585d import A7585D 
from a7585d import A7585D_REG
import time

import pyqtgraph as pg
from random import randint
from MonitorPlots import *



class tab_SiPM_HV_config(object):

    def __init__(self, run_config, status, MainWindow, devices):
        self.run_config = run_config
        self.status = status
        self.widgetList = []
        self.hv = A7585D()
        self.hv2 = A7585D()
        self.portsList = devices.caen_hv_devices
        print("Ports: {}".format(self.portsList))
        self.hv_logfile_name = 'hv_log.csv'
        self.hv2_logfile_name = 'hv2_log.csv'
        self.setup_UI(MainWindow)


    def setup_UI(self, MainWindow):

        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)
        
        buttonWindow = QtWidgets.QWidget()
        buttonWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout = QtWidgets.QGridLayout(buttonWindow)

        row = 0
        column = 0
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Port")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)


        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Open")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)


        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Max V(V)")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Max I(mA)")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Ramp(V/s)")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Out Volt (V)")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Param. Set")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        column += 1
        self.label_vol = QtWidgets.QLabel()
        self.label_vol.setText("Out Enable")
        self.gridLayout.addWidget(self.label_vol, row, column, 1, 1)

        row += 1
        self.setup_UI_hv1(row)
        row += 1
        self.setup_UI_hv2(row)

        sectionLayout.addWidget(buttonWindow)


        # Add a timer to simulate new temperature measurements

        self.monitor_plots = MonitorPlots(self.status)
        self.monitor_plots.make_plot("HV1 Voltage vs Time", "Voltage (V)")
        self.monitor_plots.make_plot("HV1 Current vs Time", "Current (mA)", use_log = True)
        self.monitor_plots.make_plot("HV2 Voltage vs Time", "Voltage (V)")
        self.monitor_plots.make_plot("HV2 Current vs Time", "Current (mA)", use_log = True)
        self.monitor_plots.request_monitor_data.connect(self.update_plot)
        sectionLayout.addWidget(self.monitor_plots.get_layout_widget())

        row += 1
        self.gridLayout.addWidget(self.monitor_plots.start_button, row, 0, 1, 1)
        self.gridLayout.addWidget(self.monitor_plots.stop_button, row, 1, 1, 1)



    def setup_UI_hv1(self, row):

        column = 0
        self.comboBox_dev1_Port = QtWidgets.QComboBox()
        self.comboBox_dev1_Port.addItems(self.portsList)
        self.gridLayout.addWidget(self.comboBox_dev1_Port, row, column, 1, 1)
        try:
            self.comboBox_dev1_Port.setCurrentIndex(
                self.portsList.index("/dev/CAEN_Front_Bias_21756"))
        except Exception as e:
            pass


        column += 1
        self.pushButton_open_dev1 = QtWidgets.QPushButton()
        self.pushButton_open_dev1.setText("Open Dev1")
        self.pushButton_open_dev1.clicked.connect(self.open_dev1)
        self.gridLayout.addWidget(self.pushButton_open_dev1, row, column, 1, 1)

        column += 1
        self.lineEdit_MaxV_dev1 = QtWidgets.QLineEdit()
        self.lineEdit_MaxV_dev1.setText('50.0')
        self.gridLayout.addWidget(self.lineEdit_MaxV_dev1,row, column, 1, 1)

        column += 1
        self.lineEdit_MaxI_dev1 = QtWidgets.QLineEdit()
        self.lineEdit_MaxI_dev1.setText('0.5')
        self.gridLayout.addWidget(self.lineEdit_MaxI_dev1,row, column, 1, 1)

        column += 1
        self.lineEdit_Ramp_dev1 = QtWidgets.QLineEdit()
        self.lineEdit_Ramp_dev1.setText('2.0')
        self.gridLayout.addWidget(self.lineEdit_Ramp_dev1,row, column, 1, 1)

        column += 1
        self.lineEdit_TargetV_dev1 = QtWidgets.QLineEdit()
        self.lineEdit_TargetV_dev1.setText('42.5')
        self.gridLayout.addWidget(self.lineEdit_TargetV_dev1,row, column, 1, 1)

        column += 1
        self.pushButton_set_dev1 = QtWidgets.QPushButton()
        self.pushButton_set_dev1.setText("Set Dev1")
        self.gridLayout.addWidget(self.pushButton_set_dev1, row, column, 1, 1)
        self.pushButton_set_dev1.clicked.connect(self.set_dev1)
        self.pushButton_set_dev1.setEnabled(False)

        column += 1
        self.checkBox_out_en_dev1 = QtWidgets.QCheckBox()
        self.checkBox_out_en_dev1.setChecked(False)
        self.gridLayout.addWidget(self.checkBox_out_en_dev1,row, column, 1, 1)
        self.checkBox_out_en_dev1.stateChanged.connect(self.enable_HV1)

    def setup_UI_hv2(self, row):

        column = 0
        self.comboBox_dev2_Port = QtWidgets.QComboBox()
        self.comboBox_dev2_Port.addItems(self.portsList)
        self.gridLayout.addWidget(self.comboBox_dev2_Port, row, column, 1, 1)
        try:
            self.comboBox_dev2_Port.setCurrentIndex(
                self.portsList.index("/dev/CAEN_Rear_Bias_21758"))
        except Exception as e:
            pass

        column +=1
        self.pushButton_open_dev2 = QtWidgets.QPushButton()
        self.pushButton_open_dev2.setText("Open Dev2")
        self.pushButton_open_dev2.clicked.connect(self.open_dev2)
        self.gridLayout.addWidget(self.pushButton_open_dev2, row, column, 1, 1)

        column += 1
        self.lineEdit_MaxV_dev2 = QtWidgets.QLineEdit()
        self.lineEdit_MaxV_dev2.setText('50.0')
        self.gridLayout.addWidget(self.lineEdit_MaxV_dev2,row, column, 1, 1)

        column += 1
        self.lineEdit_MaxI_dev2 = QtWidgets.QLineEdit()
        self.lineEdit_MaxI_dev2.setText('0.5')
        self.gridLayout.addWidget(self.lineEdit_MaxI_dev2,row, column, 1, 1)

        column += 1
        self.lineEdit_Ramp_dev2 = QtWidgets.QLineEdit()
        self.lineEdit_Ramp_dev2.setText('2.0')
        self.gridLayout.addWidget(self.lineEdit_Ramp_dev2,row, column, 1, 1)

        column += 1
        self.lineEdit_TargetV_dev2 = QtWidgets.QLineEdit()
        self.lineEdit_TargetV_dev2.setText('42.5')
        self.gridLayout.addWidget(self.lineEdit_TargetV_dev2,row, column, 1, 1)

        column += 1
        self.pushButton_set_dev2 = QtWidgets.QPushButton()
        self.pushButton_set_dev2.setText("Set Dev2")
        self.gridLayout.addWidget(self.pushButton_set_dev2, row, column, 1, 1)
        self.pushButton_set_dev2.clicked.connect(self.set_dev2)
        self.pushButton_set_dev2.setEnabled(False)

        column += 1
        self.checkBox_out_en_dev2 = QtWidgets.QCheckBox()
        self.checkBox_out_en_dev2.setChecked(False)
        self.gridLayout.addWidget(self.checkBox_out_en_dev2,row, column, 1, 1)
        self.checkBox_out_en_dev2.stateChanged.connect(self.enable_HV2)

 
    def update_plot(self):       

        if self.hv.ser != None:
            volt = self.get_voltage(self.hv)
            curr = self.get_current(self.hv)
            self.monitor_plots.add_point(0, volt)
            self.monitor_plots.add_point(1, curr)
            with open(self.hv_logfile_name,'a') as f:
                f.writelines(str(self.status.monitor_time)+','+str(round(volt,3))+','+str(round(curr,3))+'\n')

        if self.hv2.ser != None:
            volt = self.get_voltage(self.hv2)
            curr = self.get_current(self.hv2)
            self.monitor_plots.add_point(2, volt)
            self.monitor_plots.add_point(3, curr)
            with open(self.hv2_logfile_name,'a') as f:
                f.writelines(str(self.status.monitor_time)+','+str(round(volt,3))+','+str(round(curr,3))+'\n')

    def open_dev1(self):
        try:
            self.hv.open(self.comboBox_dev1_Port.currentText())

        except Exception as e:
            print(e)
        else:
            if self.hv.ser != None:
                try:
                    code = self.hv.get_parameter(A7585D_REG.PRODUCT_CODE)
                except Exception as e:
                    # print(e)
                    print("Product code does not match. Try another device.")
                else:
                    if code == 54:
                        print("Device1 opened")
                        print(self.hv)
                        print("Product code ="+str(self.hv.get_parameter(A7585D_REG.PRODUCT_CODE)))
                        print("Firmware ver ="+str(self.hv.get_parameter(A7585D_REG.FW_VERSION)))
                        print("Hardware ver ="+str(self.hv.get_parameter(A7585D_REG.HW_VERSION)))
                        print("Serial number="+str(self.hv.get_parameter(A7585D_REG.SERIAL_NUMBER)))
                        self.pushButton_set_dev1.setEnabled(True) 
                    else:
                        print("Product code does not match. Try another device.")
            else:
                print("Open device1 failed")



    def set_dev1(self):
        # set control output control loop mode
        # 0 Digital mode (output voltage is vtarget)
        # 1 Analog mode (output voltage is proportional to vref)
        # 2 Thermal compensation (output voltage is vtarget - Tcoef * (T - 25)
        self.hv.set_parameter(A7585D_REG.CNTRL_MODE, 0)  

        # set voltage target to 40V
        self.hv.set_parameter(A7585D_REG.V_TARGET, float(self.lineEdit_TargetV_dev1.text()))

        # set max current 1mA
        if float(self.lineEdit_MaxI_dev1.text()) > 0.5:
            print("Maximum current should not go above 0.5 mA for SiPM safety!")
        else:
            self.hv.set_parameter(A7585D_REG.MAX_I, float(self.lineEdit_MaxI_dev1.text()))

        # set max voltage (compliance) to 50V
        self.hv.set_parameter(A7585D_REG.MAX_V, float(self.lineEdit_MaxV_dev1.text()))

        # configure SiPM temperature compensation coefficient
        self.hv.set_parameter(A7585D_REG.T_COEF_SIPM, -35)

        # configure ramp speed to 5V/s
        self.hv.set_parameter(A7585D_REG.RAMP, float(self.lineEdit_Ramp_dev1.text()))

    def enable_HV1(self):
        # enable hv
        if self.checkBox_out_en_dev1.isChecked():
            self.hv.set_parameter(A7585D_REG.HV_ENABLE, 1)
            print("HV output enabled for dev1")
        else:
            self.hv.set_parameter(A7585D_REG.HV_ENABLE, 0)
            print("HV output disabled for dev1")

    

    def open_dev2(self):
        try:
            self.hv2.open(self.comboBox_dev2_Port.currentText())

        except Exception as e:
            print(e)
        else:
            if self.hv2.ser != None:
                try:
                    code = self.hv2.get_parameter(A7585D_REG.PRODUCT_CODE)
                except Exception as e:
                    # print(e)
                    print("Product code does not match. Try another device.")
                else:
                    if code == 54:
                        print("Device2 opened")
                        print(self.hv2)
                        print("Product code ="+str(self.hv2.get_parameter(A7585D_REG.PRODUCT_CODE)))
                        print("Firmware ver ="+str(self.hv2.get_parameter(A7585D_REG.FW_VERSION)))
                        print("Hardware ver ="+str(self.hv2.get_parameter(A7585D_REG.HW_VERSION)))
                        print("Serial number="+str(self.hv2.get_parameter(A7585D_REG.SERIAL_NUMBER)))
                        self.pushButton_set_dev2.setEnabled(True) 
                    else:
                        print("Product code does not match. Try another device.")

            else:
                print("Open device2 failed")

    def set_dev2(self):
        # set control output control loop mode
        # 0 Digital mode (output voltage is vtarget)
        # 1 Analog mode (output voltage is proportional to vref)
        # 2 Thermal compensation (output voltage is vtarget - Tcoef * (T - 25)
        self.hv2.set_parameter(A7585D_REG.CNTRL_MODE, 0)  

        # set voltage target to 40V
        self.hv2.set_parameter(A7585D_REG.V_TARGET, float(self.lineEdit_TargetV_dev2.text()))

        # set max voltage 1mA
        if float(self.lineEdit_MaxI_dev2.text()) > 0.5:
            print("Max current should not go above 0.5 mA for SiPM safety!")
        else:
            self.hv2.set_parameter(A7585D_REG.MAX_I, float(self.lineEdit_MaxI_dev2.text()))

        # set max voltage (compliance) to 50V
        self.hv2.set_parameter(A7585D_REG.MAX_V, float(self.lineEdit_MaxV_dev2.text()))

        # configure SiPM temperature compensation coefficient
        self.hv2.set_parameter(A7585D_REG.T_COEF_SIPM, -35)

        # configure ramp speed to 5V/s
        self.hv2.set_parameter(A7585D_REG.RAMP, float(self.lineEdit_Ramp_dev2.text()))

    def enable_HV2(self):
        # enable hv
        if self.checkBox_out_en_dev2.isChecked():
            self.hv2.set_parameter(A7585D_REG.HV_ENABLE, 1)
            print("HV output enabled for dev2")
        else:
            self.hv2.set_parameter(A7585D_REG.HV_ENABLE, 0)
            print("HV output disabled for dev2")

    def get_voltage(self,hv):
        if hv.ser != None:
            return hv.get_parameter(A7585D_REG.MON_VOUT)
        else:
            print("Error: please check SiPM HV connection")

    def get_current(self,hv):   
        if hv.ser != None:
            return hv.get_parameter(A7585D_REG.MON_IOUT)
        else:
            print("Error: please check SiPM HV connection")


        




# # set current monitor range
# # 0 low range
# # 1 high range
# # 2 auto select
# hv.set_parameter(A7585D_REG.CURRENT_RANGE, 2)


# # control pi controller (1 enable)
# hv.set_parameter(A7585D_REG.ENABLE_PI, 0)


        



