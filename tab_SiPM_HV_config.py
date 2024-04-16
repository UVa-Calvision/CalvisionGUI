from PyQt5 import QtCore, QtGui, QtWidgets
from a7585d import A7585D 
from a7585d import A7585D_REG
import time

import pyqtgraph as pg
from random import randint




class tab_SiPM_HV_config(object):

    def __init__(self, MainWindow, portsList):
        
        self.widgetList = []
        self.hv = A7585D()
        self.hv2 = A7585D()
        self.portsList = portsList
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


        row += 1
        column = 0
        self.pushButton_timer_start = QtWidgets.QPushButton()
        self.pushButton_timer_start.setText("Start Monitor")
        self.gridLayout.addWidget(self.pushButton_timer_start, row, column, 1, 1)
        self.pushButton_timer_start.clicked.connect(self.timer_start)
        self.pushButton_timer_start.setEnabled(False)

        column += 1
        self.pushButton_timer_stop = QtWidgets.QPushButton()
        self.pushButton_timer_stop.setText("Stop")
        self.gridLayout.addWidget(self.pushButton_timer_stop, row, column, 1, 1)
        self.pushButton_timer_stop.clicked.connect(self.timer_stop)
        self.pushButton_timer_stop.setEnabled(False)


        sectionLayout.addWidget(buttonWindow)


        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)


        hv1_gridLayout = pg.GraphicsLayoutWidget()
        hv1_gridLayout.setBackground('w')
        self.line_volt1 = self.plot_data(layoutWidget = hv1_gridLayout, title = "HV1 Voltage vs Time", ylabel = "Voltage (V)", use_log = False)
        self.line_curr1 = self.plot_data(layoutWidget = hv1_gridLayout, title = "HV1 Current vs Time", ylabel = "Current (mA)", use_log = True)
        # sectionLayout.addWidget(hv1_gridLayout)


        # hv2_gridLayout = pg.GraphicsLayoutWidget()
        # hv2_gridLayout.setBackground('w')
        self.line_volt2 = self.plot_data(layoutWidget = hv1_gridLayout, title = "HV2 Voltage vs Time", ylabel = "Voltage (V)", use_log = False)
        self.line_curr2 = self.plot_data(layoutWidget = hv1_gridLayout, title = "HV2 Current vs Time", ylabel = "Current (mA)", use_log = True)
        sectionLayout.addWidget(hv1_gridLayout)


        # self.gridLayoutWidget2 = QtWidgets.QWidget(MainWindow)
        # self.gridLayoutWidget2.setGeometry(QtCore.QRect(0,150,300,300))
        # self.gridLayoutWidget3 = QtWidgets.QWidget(MainWindow)
        # self.gridLayoutWidget3.setGeometry(QtCore.QRect(300,150,300,300))
        self.time1 = [0]
        self.volt1 = [0]
        self.curr1 = [0]
        # self.line_volt1=self.plot_data(x=self.time1,y=self.volt1,layoutWidget=self.gridLayoutWidget2,title="HV1 Voltage vs Time",ylabel="Voltage (V)")
        # self.line_curr1=self.plot_data(x=self.time1,y=self.curr1,layoutWidget=self.gridLayoutWidget3,title="HV1 Current vs Time",ylabel="Current (mA)",use_log=True)

        # self.gridLayoutWidget4 = QtWidgets.QWidget(MainWindow)
        # self.gridLayoutWidget4.setGeometry(QtCore.QRect(600,150,300,300))
        # self.gridLayoutWidget5 = QtWidgets.QWidget(MainWindow)
        # self.gridLayoutWidget5.setGeometry(QtCore.QRect(900,150,300,300))
        self.time2 = [0]
        self.volt2 = [0]
        self.curr2 = [0]
        # self.line_volt2=self.plot_data(x=self.time2,y=self.volt2,layoutWidget=self.gridLayoutWidget4,title="HV2 Voltage vs Time",ylabel="Voltage (V)")
        # self.line_curr2=self.plot_data(x=self.time2,y=self.curr2,layoutWidget=self.gridLayoutWidget5,title="HV2 Current vs Time",ylabel="Current (mA)",use_log=True)



    def setup_UI_hv1(self, row):

        column = 0
        self.comboBox_dev1_Port = QtWidgets.QComboBox()
        self.comboBox_dev1_Port.addItems(self.portsList)
        self.gridLayout.addWidget(self.comboBox_dev1_Port, row, column, 1, 1)
        try:
            self.comboBox_dev1_Port.setCurrentIndex(
                self.portsList.index("/dev/CAEN21756"))
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
        self.lineEdit_MaxI_dev1.setText('10.0')
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
                self.portsList.index("/dev/CAEN21758"))
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
        self.lineEdit_MaxI_dev2.setText('10.0')
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


    def plot_data(self,layoutWidget,title,ylabel,use_log=False):
        pen = pg.mkPen(color='b', width=3)
        styles = {"color": "red", "font-size": "12px"}

        plot = layoutWidget.addPlot()
        plot.setTitle(title, color = 'b', size = '10pt')
        plot.setLabel("left", ylabel, **styles)
        plot.setLabel("bottom", "Time (s)", **styles)
        plot.addLegend()
        plot.showGrid(x=True, y=True)
        if use_log:
            plot.setLogMode(y=True)

        return plot.plot([0], [0], pen=pen)

        # gridLayout = QtWidgets.QGridLayout(layoutWidget)
        # pen = pg.mkPen(color='b', width=3)
        # plot_graph = pg.PlotWidget()

        # # setCentralWidget(plot_graph)
        # gridLayout.addWidget(plot_graph,0,0,1,1)

        # plot_graph.setBackground("w")
        # 

        # # Temperature vs time dynamic plot

        # plot_graph.setTitle(title, color="b", size="10pt")
        # styles = {"color": "red", "font-size": "12px"}
        # plot_graph.setLabel("left", ylabel, **styles)
        # plot_graph.setLabel("bottom", "Time (min)", **styles)
        # plot_graph.addLegend()
        # plot_graph.showGrid(x=True, y=True)
        # # plot_graph.setYRange(20, 40)
        # if use_log:
        #     plot_graph.setLogMode(y=True)
        # 
        # # Get a line reference
        # line = plot_graph.plot(x,y,pen=pen)
        # return line

        
        # self.timer.start()

    def update_plot(self):       

        if self.hv.ser != None:
            time = self.time1[-1] + 1
            volt = self.get_voltage(self.hv)
            curr = self.get_current(self.hv)
            self.time1.append(time)
            self.volt1.append(volt)
            self.curr1.append(curr)
            self.line_volt1.setData([d/60.0 for d in self.time1[1:]], self.volt1[1:])
            self.line_curr1.setData([d/60.0 for d in self.time1[1:]], self.curr1[1:])
            with open(self.hv_logfile_name,'a') as f:
                f.writelines(str(time)+','+str(round(volt,3))+','+str(round(curr,3))+'\n')

        if self.hv2.ser != None:
            time = self.time2[-1] + 1
            volt = self.get_voltage(self.hv2)
            curr = self.get_current(self.hv2)
            self.time2.append(time)
            self.volt2.append(volt)
            self.curr2.append(curr)
            self.line_volt2.setData([d/60.0 for d in self.time2[1:]], self.volt2[1:])
            self.line_curr2.setData([d/60.0 for d in self.time2[1:]], self.curr2[1:])
            with open(self.hv2_logfile_name,'a') as f:
                f.writelines(str(time)+','+str(round(volt,3))+','+str(round(curr,3))+'\n')

        

        


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
                        self.pushButton_timer_start.setEnabled(True)
                        self.pushButton_timer_stop.setEnabled(True)
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

        # set max voltage 1mA
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
                        self.pushButton_timer_start.setEnabled(True)
                        self.pushButton_timer_stop.setEnabled(True)
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



    def timer_start(self):
        self.timer.start()

    def timer_stop(self):
        self.timer.stop()

        




# # set current monitor range
# # 0 low range
# # 1 high range
# # 2 auto select
# hv.set_parameter(A7585D_REG.CURRENT_RANGE, 2)


# # control pi controller (1 enable)
# hv.set_parameter(A7585D_REG.ENABLE_PI, 0)


        



