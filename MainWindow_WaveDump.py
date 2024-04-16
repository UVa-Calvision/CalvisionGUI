# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow_trying.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
                             QAction, QFileDialog, QApplication)
# from PyDecode import PyDeocde
# from ReviewPyDecode import ReviewPyDecode
# import decode
import sys
import time
import os
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from Worker_startWaveDump import *
# from Worker_startDecode import *
# from Worker_runDecode import *
from datetime import datetime
from datetime import date
import binascii
import time
import csv
import threading
import glob
import serial
import re
from tab_SiPM_HV_config import *
from tab_PIcontrol import *
from tab_DAQ_control import *
# from tab_digitizer_config import *
from tab_calibrate import tab_calibrate


timestr = time.strftime("%Y-%m-%d-%H%M%S")
flag_wavedump = 0

class Ui_MainWindow(object):

    def __init__(self):
        self.path = ''
        self.signalPath = '../SignalFiles/'
        self.runCommand_file = self.signalPath + 'runCommand_file.txt'
        self.configFile = self.path + './WaveDumpConfig_X742_' #will later add device number and .txt
        self.angleFile = self.path + 'WDCurrentAngle.txt'
        self.decodeSignalFile = self.signalPath + "decodeSignal.txt"
        self.runFile = self.path + 'WDCurrentRun.txt'
        self.serial_port = 0

    

    def emptyFile(self):
        with open(self.runCommand_file, 'w') as f:
            f.write('')
        with open(self.decodeSignalFile, 'w') as f:
            f.write("%i" % 0)
    
    portsList = []
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports(include_links=True)
        for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))
            portsList.append(port)
    except ImportError:
        print("No ports avalible")

    # decode:PyDeocde
    WDstarted = False
    configSetup = []
    configSetupLabels = []
    checkBoxList = []
    startevery = 0
    file_name = ""
    trigIndex = 0

    numDevices = 2
    
    current_run = 0
    current_run_text = '0'

    current_angle = 0
    current_angle_text = '0'


    configDict = {
        "OPEN": "USB 0 0",
        "RECORD_LENGTH": 1024,
        "POST_TRIGGER": 50,
        "PULSE_POLARITY": "POSITIVE",
        "EXTERNAL_TRIGGER": "DISABLED",
        "FAST_TRIGGER": "ACQUISITION_ONLY",
        "ENABLED_FAST_TRIGGER_DIGITIZING": "YES",
        "CORRECTION_LEVEL": "AUTO",
        "DRS4_FREQUENCY": "5 GHz",
        "OUTPUT_FILE_FORMAT": "BINARY",
        "OUTPUT_FILE_HEADER": "YES",
        "TEST_PATTERN": "NO",
        "FPIO_LEVEL": "NIM",
        "ENABLE_INPUT": "NO",
        "DC_OFFSET": 0,
        "[0]": "",
        "0ENABLE_INPUT": "YES",
        "0DC_OFFSET": 0,
        "0GRP_CH_DC_OFFSET": [0, 0, 0, 0, 0, 0, 0, 0],
        "[1]": "",
        "1ENABLE_INPUT": "YES",
        "1DC_OFFSET": 0,
        "1GRP_CH_DC_OFFSET": [0, 0, 0, 0, 0, 0, 0, 0],
        "[TR0]": "",
        "2DC_OFFSET": 32768,
        "TRIGGER_THRESHOLD": 24894
    }

    configDictOptions = {
        "OPEN": "USB 0 0",
        "RECORD_LENGTH": 1024,
        "POST_TRIGGER": {"min": 0, "max": 100},
        "PULSE_POLARITY": ["POSITIVE", "NEGATIVE"],
        "EXTERNAL_TRIGGER": ["DISABLED", "ACQUISITION_ONLY", "ACQUISITION_AND_TRGOUT"],
        "FAST_TRIGGER": ["DISABLED", "ACQUISITION_ONLY"],
        "ENABLED_FAST_TRIGGER_DIGITIZING": ["YES", "NO"],
        "CORRECTION_LEVEL": ["AUTO"],           #FIX
        "DRS4_FREQUENCY": ["5 GHz", "2.5 GHz", "1 GHz", "750 MHz"],
        "OUTPUT_FILE_FORMAT": ["BINARY", "ASCII", "BOTH"],
        "OUTPUT_FILE_HEADER": ["YES", "NO"],
        "TEST_PATTERN": ["YES", "NO"],
        "FPIO_LEVEL": ["NIM", "TTL"],
        "ENABLE_INPUT": ["YES", "NO"],
        "DC_OFFSET": {"min": -50, "max": 50},
        "[0]": "",
        "0ENABLE_INPUT": ["YES", "NO"],
        "0DC_OFFSET": {"min": -50, "max": 50},
        "0GRP_CH_DC_OFFSET": [3, 0, 0, 0, 0, 0, 0, 0],
        "[1]": "",
        "1ENABLE_INPUT": ["YES", "NO"],
        "1DC_OFFSET": {"min": -50, "max": 50},
        "1GRP_CH_DC_OFFSET": [3, 0, 0, 0, 0, 0, 0, 0],
        "[TR0]": "",
        "2DC_OFFSET": {"min": 0, "max": 65535},
        "TRIGGER_THRESHOLD": {"min": 0, "max": 65535}
    }

    valueDict = {
        "QUIT": 0,
        "RELOADCONF": 0,
        "STARTSTOP": 0,
        "TRIGGER": 0,
        "ENTRIGGER": 0,
        "WRITEFILE": 0,
        "CONTWRITEFILE": 0,
        "PLOTEVENT": 0,
        "CONTPLOTEVENT": 0,
        "SETCHANNELEN": '11111111',
        "NEXTGRPEN": 0
    }

    trigger_preset_dic = {
        "NONE": '',
        "ECL": 26214,
        "NIM": 20934,
        "Negative signal (V =0/n400mV)": 23574,
        "Negative signal (V =0/n200mV)": 24894
    }

    deviceValueDic = []
    deviceConfigDic = []
    deviceConfigSetup = []
    deviceConfigSetupLabels = []
    deviceConfigTabs = []
    deviceComboBox_triggerPreSet = []
    deviceCheckBoxList = []
    chnl_controls = []

    root_files = {}
    def setupForDeviceNum(self):
        for i in range(self.numDevices):
            self.deviceValueDic.append(self.valueDict)
            self.deviceConfigDic.append(self.configDict)
            self.deviceConfigSetup.append([])
            self.deviceConfigSetupLabels.append([])
            self.deviceCheckBoxList.append([])
            self.chnl_controls.append([])


    def saveCurrentRun(self):
        with open(self.runFile, 'w') as f:
            f.write(str(self.current_run) + '\n')
            f.write(self.current_run_text)

    def findCurrentRun(self):
        with open(self.runFile, 'r') as f:
            self.current_run = int(f.readline())
            self.current_run_text = f.readline()
    
    def setCurrentRun(self):
        self.pushButton_setNewRun.setEnabled(False)
        newRunNum = self.QSpinBox_runNum.value()
        self.current_run = newRunNum
        self.current_run_text = (str)(newRunNum)
        self.saveCurrentRun()
        self.pushButton_setNewRun.setEnabled(True)

    def angleChange(self):
        if self.serial_port!=0:
            if self.current_angle != self.QSpinBox_angle.value():
                self.pushButton_updateAngle.setEnabled(True)
            else:
                self.pushButton_updateAngle.setEnabled(False)

    def saveCurrentAngle(self):
        with open(self.angleFile, 'w') as f:
            f.write(str(self.current_angle) + '\n')
            f.write(self.current_angle_text)

    def findCurrentAngle(self):
        with open(self.angleFile, 'r') as f:
            self.current_angle = int(f.readline())
            self.current_angle_text = f.readline()

    def updateAngle(self):
        if self.serial_port==0:
            print("UART not enabled.")
        else:
            self.pushButton_updateAngle.setEnabled(False)
            new_angle = self.QSpinBox_angle.value()
            if self.current_angle != new_angle:
                change = new_angle - self.current_angle
                if change < 0:
                    change = abs(change)
                    command = '<1,'+str(change)+',0>'
                else:
                    change = abs(change)
                    command = '<0,'+str(change)+',0>'


                
                print("Org.angle = "+str(self.current_angle))
                print("New angle = "+str(new_angle))
                print("Angle change = " + str(new_angle - self.current_angle))
                #hex_command = bytes('', 'utf-8')
                #for i in command:
                    #hex_command += "\\x"
                    #hex_command += i.encode('utf-8').hex()
                    #hex_command += bytes(i, 'utf-8')
                hex_command = bytearray(command, 'utf-8')
                self.current_angle = new_angle
                print("Sending command: " + command)
                self.serial_port.write(hex_command)
                self.serial_port.flush()
                time.sleep(0.05)
                while(1):
                    data = self.serial_port.readline()
                    if len(data)!=0:
                        print("UART read back:"+str(data))
                    else:
                        break
                
                
                if new_angle == 0:
                    self.current_angle_text = str(abs(new_angle))
                elif new_angle < 0:
                    self.current_angle_text = 'n' + str(abs(new_angle))
                else:
                    self.current_angle_text = 'p' + str(abs(new_angle))
                self.saveCurrentAngle()
            else:
                print("No angle change!")

    # def writeConfigFile(self):
    #     for deviceNum in range(self.numDevices):
    #         self.tab_digitizer_config.export_config(deviceNum)

    def writeConfigFile(self):
        files = []
        for deviceNum in range(self.numDevices):
            file = self.configFile + str(deviceNum) + ".txt"
            files.append(file)
            with open(file, 'w') as f:
                f.write("[COMMON]" + '\n')
                for x in range(0, len(self.configDict)):
                    if "GRP_CH_DC_OFFSET" == self.deviceConfigSetupLabels[deviceNum][x].text():
                        r = ""
                        for a in range(0, 8):
                            r += str(self.deviceConfigSetup[deviceNum][x][a].value())
                            if a < 7:
                                if flag_wavedump:
                                    r += ", "
                                else:
                                    r += " "
                        f.write("GRP_CH_DC_OFFSET" + " " + r + '\n')
                        print("GRP_CH_DC_OFFSET" + " " + r)
                    elif "DRS4_FREQUENCY" == self.deviceConfigSetup[deviceNum][x].accessibleName():
                        f.write(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + str(self.deviceConfigSetup[deviceNum][x].currentIndex()) + '\n')
                        print(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + str(self.deviceConfigSetup[deviceNum][x].currentIndex()))
                    elif isinstance(self.deviceConfigSetup[deviceNum][x], QLabel):
                        f.write(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + self.deviceConfigSetup[deviceNum][x].text() + '\n')
                        print(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + self.deviceConfigSetup[deviceNum][x].text())
                    elif isinstance(self.deviceConfigSetup[deviceNum][x], QSpinBox):
                        f.write(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + str(self.deviceConfigSetup[deviceNum][x].value()) + '\n')
                        print(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + str(self.deviceConfigSetup[deviceNum][x].value()))
                    else:
                        f.write(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + self.deviceConfigSetup[deviceNum][x].currentText() + '\n')
                        print(self.deviceConfigSetup[deviceNum][x].accessibleName() + " " + self.deviceConfigSetup[deviceNum][x].currentText())
        return files

    def copyConfigFile(self, file_name):
        # username = os.getlogin()
        # userPath = os.path.expanduser('~')
        # filepath = os.path.join(userPath, 'WaveDump')
        filepath = '../WaveDumpData/'
        filepath = os.path.join(filepath, file_name)
        #print(os.listdir(filepath))
        # '~'+'/Wavedum'
        print(filepath)
        os.mkdir(filepath)
        for deviceNum in range(self.numDevices):
            file = self.configFile + str(deviceNum) + ".txt"
            newfilepath = os.path.join(filepath, 'ConfigFile_%i.txt' %deviceNum)
            with open(newfilepath, 'w') as f:
                with open(file,'r') as a:
                    tmp = a.readlines()
                    f.writelines(tmp)

        #shutil.copyfile(filepath, self.configFile)

    def sendChar(self, dic):
        #valueDict.update({dic: 1})
        if dic == "RELOADCONF" and self.valueDict["STARTSTOP"]:
            print("WARNING: PLEASE STOP Start/Stop acquisition!!!!")
        elif dic == "STARTSTOP" and self.valueDict["STARTSTOP"] == 1:
            with open(self.runCommand_file, 'w') as f:
                today = date.today()
                current_date = today.strftime("%Y%m%d")
                now = datetime.now()
                current_time = now.strftime("%H%M%S")
                #angle = self.lineEdit_Angle.text()
                crystalType = self.lineEdit_Crystal.text()

                self.file_name = "run_" + self.current_run_text + "_ang_" + self.current_angle_text + "deg_" + crystalType + "_" + current_date + "_" + current_time
                self.copyConfigFile(self.file_name)
                f.write(dic + " " + str(self.valueDict[dic]) + " " + self.file_name)
                print(dic + " " + str(self.valueDict[dic]) + " " + self.file_name)
        else:
            #self.writeConfigFile()
            with open(self.runCommand_file, 'w') as f:
                f.write(dic + " " + str(self.valueDict[dic]))
                print(dic + " " + str(self.valueDict[dic]))


    def enDisCheckBox(self, dic):
        newValue = 1 ^ self.valueDict[dic]
        self.valueDict.update({dic: newValue})
        if self.startevery == 0:
            self.sendChar(dic)
        return newValue

    def chEnCheckBox(self):
        
        strValHex = ""
        for device in range(self.numDevices):
            ens = ""
            for i in self.deviceCheckBoxList[device]:
                if i.isChecked():
                    ens += '1'
                else:
                    ens += '0'
            # self.deviceValueDic[device].update({"SETCHANNELEN": ens})
            valHex = '0x'+format(int(ens, 2),'x')[0:2].zfill(2)
            strValHex += " " + str(valHex)
        
        with open(self.runCommand_file, 'w') as f:
            f.write("SETCHANNELEN" + strValHex)
            print("SETCHANNELEN" + strValHex)

    #@QtCore.pyqtSlot(int)
    def updateConfigDict(self, val):
        print(val)

        combo = self.sender()
        #dic = combo.accessibleName()
        print("update: "  + val)
        self.configDict.update({dic: val})

    def updateConfigDictComboBox(self, dic):
        self.configDict.update({dic: val})

    def setTriggerTR0(self):
        for device in range(self.numDevices):
            if self.deviceComboBox_triggerPreSet[device].currentText() != "NONE":
                self.deviceConfigSetup[device][self.trigIndex].setValue(self.trigger_preset_dic[self.deviceComboBox_triggerPreSet[device].currentText()])

    def changeTriggerTr0(self, device):
        for device in range(self.numDevices):
            if self.trigger_preset_dic[self.deviceComboBox_triggerPreSet[device].currentText()] != self.deviceConfigSetup[device][self.trigIndex].value():
                self.deviceComboBox_triggerPreSet[device].setCurrentIndex(0)

    def startEverything(self):
        # if self.numDevices != self.listUSBDevices():
        #     self.label_ImptMess.setText("There are not the correct number of devices connected.")
        #     self.label_ImptMess.setStyleSheet("color : red")
        #     QApplication.processEvents()
        #     print("There are not the correct number of devices connected.")
        #     return
        # if (not self.WDstarted):
        #     self.label_ImptMess.setText("Please wait while everything is setup.")
        #     self.label_ImptMess.setStyleSheet("color : red")
        #     # QApplication.processEvents()
        #     self.start_WaveDump()
        
        today = date.today()
        current_date = today.strftime("%Y%m%d")
        now = datetime.now()
        current_time = now.strftime("%H%M%S")
        #angle = self.lineEdit_Angle.text()
        crystalType = self.lineEdit_Crystal.text()

        self.file_name = "run_" + self.current_run_text + "_ang_" + self.current_angle_text + "deg_" + crystalType + "_" + current_date + "_" + current_time
        self.copyConfigFile(self.file_name)
        # # self.decode = PyDeocde(self.file_name, self.numDevices)
        # # self.decode.start(self.file_name)
        # self.start_Decode()

        self.pushButton_START.setEnabled(False)
        self.startevery = 1
        self.checkBox_s.setChecked(True)
        self.enDisCheckBox("CONTWRITEFILE")
        #self.checkBox_capW.setChecked(True)

        time.sleep(0.5)
        while os.path.getsize(self.runCommand_file) != 0:
            time.sleep(0.5)
        time.sleep(0.5)

        with open(self.runCommand_file, 'w') as f:
            f.write("STARTEVERY" + " " + str(self.valueDict["STARTSTOP"]) + " " + self.file_name)
            print("STARTEVERY" + " " + str(self.valueDict["STARTSTOP"]) + " " + self.file_name)
        #self.start_Decode(file_name)
        self.startevery = 0
        
        print(self.runCommand_file)
        self.label_ImptMess.setText("Ready to collect data now.")
        self.label_ImptMess.setStyleSheet("color : green")
        self.pushButton_STOP.setEnabled(True)

    def stopEverything(self):
        
        # self.label_ImptMess.setText("Please wait while everything closes and an analysis is run.")
        # self.label_ImptMess.setStyleSheet("color : red")
        # QApplication.processEvents()
        self.startevery = 1
        self.checkBox_s.setChecked(False)
        self.enDisCheckBox("CONTWRITEFILE")
        with open(self.runCommand_file, 'w') as f:
            f.write("STOPEVERY 0")
            print("STOPEVERY 0")

        self.WDstarted = False
        #update run number
        self.current_run += 1
        self.current_run_text = str(self.current_run)
        self.QSpinBox_runNum.setValue(self.current_run)
        self.saveCurrentRun()
        # QApplication.processEvents()
        
        #self.decode.close()
        # print("End monitoring")
        #self.threadDecode.exit()
        self.startevery = 0
        # self.decode.stopTimer()
        # del self.decode
        # self.worker_startDec.finish()

        # self.updateHistList
        # self.externalDecode()
        # self.label_ImptMess.setText("Analysis is done.")
        # self.label_ImptMess.setStyleSheet("color : green")

        self.pushButton_START.setEnabled(False)
        self.pushButton_startWD.setEnabled(True)
        time.sleep(2)
        # while os.path.getsize(self.runCommand_file) != 0:
        #     time.sleep(0.5)
        self.checkBox_capP.setChecked(False)
    
    def WDQuit(self):
        if (not self.pushButton_START.isEnabled()):
            self.label_ImptMess.setText("Wave Dump quit unexpectedly. Please wait while everything closes and an analysis is run.")
            # QApplication.processEvents()
            self.startevery = 1
            self.checkBox_s.setChecked(False)
            self.WDstarted = False
            #update run number
            self.current_run += 1
            self.current_run_text = str(self.current_run)
            self.QSpinBox_runNum.setValue(self.current_run)
            self.saveCurrentRun()
            # QApplication.processEvents()
            
            #self.decode.close()
            print("End monitoring")
            #self.threadDecode.exit()
            self.startevery = 0
            # self.decode.stopTimer()
            # del self.decode
            
            self.worker_startDec.finish()

            self.externalDecode()
            self.label_ImptMess.setText("Analysis is done.")
            self.label_ImptMess.setStyleSheet("color : green")

    def externalDecode(self):
        # decode.main(self.file_name,self.numDevices)
        self.pushButton_START.setEnabled(True)
        self.run_externalDecode()
        self.updateHistList()
        print("Done with analysis.")
        
    
    def updateHistList(self):
        self.comboBox_pastGraphs.clear()
        self.rootFileSearch()
        self.comboBox_pastGraphs.addItems(self.root_files)
        self.comboBox_pastGraphs.setCurrentIndex(0)
    
    def reviewHist(self):
        print("trying to review")
        file = self.root_files[self.comboBox_pastGraphs.currentText()]
        print(file)
        self.reviewDecode = ReviewPyDecode(self.comboBox_pastGraphs.currentText(), file)
        self.pushButton_closePastHist.setEnabled(True)
        #print(file)

    def rootFileSearch(self):
        filepath = '../WaveDumpData/'
        rootFiles = []
        files = glob.glob(filepath + '**/*.root')
        # for file in files:
        #     print(file)
        files.sort(reverse=True)
        for file in files:
            new = file[16:file.rfind('/')]
            rootFiles.append(new)
            self.root_files.update({new:file})
        
        # for file in rootFiles:
        #     print(file)

    def addDevice(self):
        self.numDevices += 1
        self.label_numDevInt.setText(str(self.numDevices))

        #fix lists
        self.deviceValueDic.append(self.valueDict)
        self.deviceConfigDic.append(self.configDict)
        self.deviceConfigSetup.append([])
        self.deviceConfigSetupLabels.append([])
        self.deviceCheckBoxList.append([])

        #configuration tabs
        self.deviceConfigTabs.append(self.setupConfigureUI(self.numDevices - 1))
        self.deviceConfigTabWidget.addTab(self.deviceConfigTabs[self.numDevices - 1], "Device %i"%(self.numDevices - 1))

        #chnl enables
        self.deviceEnableControlRows.append(self.chnlEnRow((self.numDevices - 1)))
        self.deviceScrollForm.addRow("Device %i" %(self.numDevices - 1), self.deviceEnableControlRows[(self.numDevices - 1)])


    
    def removeDevice(self):
        self.numDevices -= 1
        self.label_numDevInt.setText(str(self.numDevices))

        #configuration tabs
        self.deviceConfigTabs.pop()
        self.deviceConfigTabWidget.removeTab(self.numDevices)

        #chnl enables
        self.deviceEnableControlRows.pop()
        self.deviceScrollForm.removeRow(self.numDevices)

        #fix lists
        self.deviceValueDic.pop()
        self.deviceConfigDic.pop()
        self.deviceConfigSetup.append([])
        self.deviceConfigSetupLabels.pop()
        self.deviceCheckBoxList.pop()
    
    def setupConfigureUI(self, device):
        self.deviceConfigWidget = QtWidgets.QWidget()
        #self.deviceConfigWidget.setGeometry(QtCore.QRect(20, 20, 860, 330))
        self.gridLayout_DAQ = QtWidgets.QGridLayout(self.deviceConfigWidget)
        
        i = 0
        row =0
        column = 0

        for key in self.configDict:
            if self.configDict[key] == "":
                row += 1
                column = 0
            if key == "OPEN":
                self.deviceConfigSetupLabels[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetupLabels[device][i], row, column, 1, 1)
                column += 1

                self.deviceConfigSetup[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetup[device][i], row, column, 1, 1)
                self.deviceConfigSetup[device][i].setText("USB "+str(device)+" 0")
                self.deviceConfigSetupLabels[device][i].setText(key)
                self.deviceConfigSetup[device][i].setAccessibleName(key)
            elif key == "RECORD_LENGTH" or (type(self.configDict[key]) is str and self.configDict[key] == ""):
                self.deviceConfigSetupLabels[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetupLabels[device][i], row, column, 1, 1)
                column += 1

                self.deviceConfigSetup[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetup[device][i], row, column, 1, 1)
                self.deviceConfigSetup[device][i].setText(str(self.configDict[key]))
                if key[0] == "0" or key[0] == "1" or key[0] == "2":
                    self.deviceConfigSetupLabels[device][i].setText(key[1:])
                    self.deviceConfigSetup[device][i].setAccessibleName(key[1:])
                else:
                    self.deviceConfigSetupLabels[device][i].setText(key)
                    self.deviceConfigSetup[device][i].setAccessibleName(key)

            elif key[1:] == "GRP_CH_DC_OFFSET":
                row += 1
                column = 0
                self.deviceConfigSetupLabels[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetupLabels[device][i], row, column, 1, 1)
                self.deviceConfigSetupLabels[device][i].setText(key[1:])
                m = []

                for a in range(0, 8):
                    column += 1
                    m.append(QtWidgets.QSpinBox(self.deviceConfigWidget))
                    self.gridLayout_DAQ.addWidget(m[a], row, column, 1, 1)
                    m[a].setAccessibleName("dc_" + str(a+1))
                    m[a].setRange(-50, 50)
                    m[a].setValue(self.configDict[key][a])
                self.deviceConfigSetup[device].append(m)
                row += 1
                column = 0
            elif type(self.configDictOptions[key]) is dict:
                self.deviceConfigSetupLabels[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetupLabels[device][i], row, column, 1, 1)
                column += 1

                self.deviceConfigSetup[device].append(QtWidgets.QSpinBox(self.deviceConfigWidget))
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetup[device][i], row, column, 1, 1)
                self.deviceConfigSetup[device][i].setRange(self.configDictOptions[key]["min"], self.configDictOptions[key]["max"])
                self.deviceConfigSetup[device][i].setValue(self.configDict[key])

                if key[0] == "0" or key[0] == "1" or key[0] == "2":
                    self.deviceConfigSetupLabels[device][i].setText(key[1:])
                    self.deviceConfigSetup[device][i].setAccessibleName(key[1:])
                else:
                    self.deviceConfigSetupLabels[device][i].setText(key)
                    self.deviceConfigSetup[device][i].setAccessibleName(key)
            elif type(self.configDict[key]) is str:
                self.deviceConfigSetupLabels[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetupLabels[device][i], row, column, 1, 1)
                self.deviceConfigSetupLabels[device][i].setText(key)
                column += 1

                self.deviceConfigSetup[device].append(QtWidgets.QComboBox(self.deviceConfigWidget))
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetup[device][i], row, column, 1, 1)
                self.deviceConfigSetup[device][i].setAccessibleName(key)
                self.deviceConfigSetup[device][i].addItems(self.configDictOptions[key])
                self.deviceConfigSetup[device][i].setCurrentIndex(
                    self.configDictOptions[key].index(self.configDict[key]))
                if key[0] == "0" or key[0] == "1" or key[0] == "2":
                    self.deviceConfigSetupLabels[device][i].setText(key[1:])
                    self.deviceConfigSetup[device][i].setAccessibleName(key[1:])
                    if key[1:] == "ENABLE_INPUT":
                        self.chnl_controls[device].append(self.deviceConfigSetup[device][i])
                else:
                    self.deviceConfigSetupLabels[device][i].setText(key)
                    self.deviceConfigSetup[device][i].setAccessibleName(key)
            else:
                print("something's wrong...")
                self.deviceConfigSetupLabels[device].append(QtWidgets.QLabel())
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetupLabels[device][i], row, column, 1, 1)
                self.deviceConfigSetupLabels[device][i].setText(key)
                column += 1

                self.deviceConfigSetup[device].append(QtWidgets.QComboBox(self.deviceConfigWidget))
                self.gridLayout_DAQ.addWidget(self.deviceConfigSetup[device][i], row, column, 1, 1)
                self.deviceConfigSetup[device][i].setAccessibleName(key)
                self.deviceConfigSetup[device][i].addItem("NOPE")
                self.deviceConfigSetup[device][i].setCurrentIndex(0)

            if key == "TRIGGER_THRESHOLD":
                self.deviceConfigSetup[device][i].valueChanged.connect(self.changeTriggerTr0)
                self.trigIndex = i

            i += 1
            column += 1
            if i % 4 == 0:
                row += 1
                column = 0
        comboBox_triggerPreSet = QtWidgets.QComboBox(self.deviceConfigWidget)
        self.gridLayout_DAQ.addWidget(comboBox_triggerPreSet, row, column, 1, 3)
        comboBox_triggerPreSet.setAccessibleName('Trigger_Preset')
        comboBox_triggerPreSet.addItems(self.trigger_preset_dic)
        comboBox_triggerPreSet.setCurrentIndex(0)
        comboBox_triggerPreSet.currentIndexChanged.connect(self.setTriggerTR0)
        self.deviceComboBox_triggerPreSet.append(comboBox_triggerPreSet)
        return self.deviceConfigWidget
    
    def listUSBDevices(self):
        count = 0
        device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = subprocess.check_output("lsusb")
        devices = []
        for i in df.split(b'\n'):
            if i:
                info = device_re.match(i)
                if info:
                    dinfo = info.groupdict()
                    dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                    devices.append(dinfo)
                    if b"CAEN" in info['tag']:
                        count += 1
        print(devices)
        return count
        
    def generalSettingsUI(self):
        columnMax = 12
        columnWids = []

        self.gridLayoutWidget_generalSettings = QtWidgets.QWidget(self.centralwidget)
        self.gridLayout_generalSettings = QtWidgets.QGridLayout(self.gridLayoutWidget_generalSettings)
        self.gridLayout_generalSettings.setVerticalSpacing(20)

        row = 0
        self.label_guiAngleCntl = QtWidgets.QLabel()
        self.label_guiAngleCntl.setText("GUI Angle Control")
        self.label_guiAngleCntl.setAlignment(QtCore.Qt.AlignCenter)
        self.label_guiAngleCntl.setStyleSheet("background-color : lightblue")
        columnWids.append(self.label_guiAngleCntl)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_generalSettings.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []
        row += 1

        self.label_guiAnglePort = QtWidgets.QLabel()
        self.label_guiAnglePort.setText("Port for Angle Control")
        columnWids.append(self.label_guiAnglePort)

        self.comboBox_AnglePort = QtWidgets.QComboBox(self.gridLayoutWidget_generalSettings)
        self.comboBox_AnglePort.setAccessibleName("ports")
        self.comboBox_AnglePort.addItems(self.portsList)
        try:
            self.comboBox_AnglePort.setCurrentIndex(
                self.portsList.index("/dev/ROTOR"))
        except ValueError:
            pass
        columnWids.append(self.comboBox_AnglePort)

        # self.pushButton_guiPortsCheck = QtWidgets.QPushButton(self.gridLayoutWidget_generalSettings)
        # self.pushButton_guiPortsCheck.setText("Refresh avalible ports")
        # self.pushButton_guiPortsCheck.clicked.connect(self.checkAnglePort)
        # columnWids.append(self.pushButton_guiPortsCheck)
        
        self.label_guiAngleEN = QtWidgets.QLabel()
        self.label_guiAngleEN.setText("Enable GUI Angle Control")
        columnWids.append(self.label_guiAngleEN)

        self.checkbox_guiAngleCntl = QtWidgets.QCheckBox()
        self.checkbox_guiAngleCntl.setCheckState(False)
        self.checkbox_guiAngleCntl.stateChanged.connect(self.setupAnglePort)
        columnWids.append(self.checkbox_guiAngleCntl)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_generalSettings.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []
        row += 1

        self.label_guiDevCntl = QtWidgets.QLabel()
        self.label_guiDevCntl.setText("Device Settings")
        self.label_guiDevCntl.setAlignment(QtCore.Qt.AlignCenter)
        self.label_guiDevCntl.setStyleSheet("background-color : lightblue")
        columnWids.append(self.label_guiDevCntl)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_generalSettings.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []
        row += 1

        self.label_numDev = QtWidgets.QLabel()
        self.label_numDev.setText("Number of Devices")
        columnWids.append(self.label_numDev)

        self.label_numDevInt = QtWidgets.QLabel()
        self.label_numDevInt.setText(str(self.numDevices))
        columnWids.append(self.label_numDevInt)

        self.pushButton_addDevice = QtWidgets.QPushButton(self.gridLayoutWidget_generalSettings)
        self.pushButton_addDevice.setText("Add Device")
        self.pushButton_addDevice.clicked.connect(self.addDevice)
        columnWids.append(self.pushButton_addDevice)

        self.pushButton_removeDevice = QtWidgets.QPushButton(self.gridLayoutWidget_generalSettings)
        self.pushButton_removeDevice.setText("Remove Device")
        self.pushButton_removeDevice.clicked.connect(self.removeDevice)
        columnWids.append(self.pushButton_removeDevice)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_generalSettings.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

    def setupAnglePort(self):
        # self.ports = serial.tools.list_ports.comports()
        # for port, desc, hwid in sorted(self.ports):
        #     print("{}: {} [{}]".format(port, desc, hwid))
        if (self.checkbox_guiAngleCntl.checkState()):
            port = self.comboBox_AnglePort.currentText()
            if len(port):
                self.serial_port = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE, timeout=0.1)
                print("Opening port: "+str(self.serial_port))
                self.QSpinBox_angle.setEnabled(True)
            else:
                print("No USB devices found.")
                self.QSpinBox_angle.setEnabled(False)
                self.pushButton_updateAngle.setEnabled(False)
        else:
            print("Closing port")
            self.serial_port.close()
            print(self.serial_port)
            self.serial_port = 0
            self.QSpinBox_angle.setEnabled(False)
            self.pushButton_updateAngle.setEnabled(False)



    def setupRunUI(self):
        rowMax = 10
        columnMax = 12
        rowCount = 0
        columnWids = []

        self.gridLayoutWidget_RunChanges = QtWidgets.QWidget(self.centralwidget)
        #self.gridLayoutWidget_RunChanges.setGeometry(QtCore.QRect(20, 20, 860, 330))
        self.gridLayout_RunChanges = QtWidgets.QGridLayout(self.gridLayoutWidget_RunChanges)
        
        row = 0
        rowCount += 1
        column = 0
        self.pushButton_startWD = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        self.pushButton_startWD.setText("StartWD")
        self.pushButton_startWD.clicked.connect(self.start_WaveDump)
        columnWids.append(self.pushButton_startWD)
        
        

        # row += 2
        # column = 0
        # self.pushButton_refresh = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_refresh, row, column, 1, 2)
        # self.pushButton_refresh.setText("Run analysis")
        # self.pushButton_refresh.clicked.connect(self.externalDecode)

        # column += 2
        self.pushButton_generateConfigFile = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        self.pushButton_generateConfigFile.setText("Generate Configuration File")
        self.pushButton_generateConfigFile.clicked.connect(self.writeConfigFile)
        columnWids.append(self.pushButton_generateConfigFile)

        # column += 2
        self.pushButton_Quit = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        self.pushButton_Quit.setText("Quit")
        self.pushButton_Quit.clicked.connect(lambda: self.sendChar("QUIT"))
        columnWids.append(self.pushButton_Quit)
        
        # column += 2
        self.pushButton_R = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        self.pushButton_R.setText("Reload configuration file and restart")
        self.pushButton_R.clicked.connect(lambda: self.sendChar("RELOADCONF"))
        columnWids.append(self.pushButton_R)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

        row += 1
        self.label_chip_no = QtWidgets.QLabel()
        #self.gridLayout_RunChanges.addWidget(self.label_chip_no, row, column, 1, 2)
        self.label_chip_no.setText("Angle")
        columnWids.append(self.label_chip_no)

        #self.lineEdit_Angle = QtWidgets.QLineEdit(self.gridLayoutWidget_RunChanges)
        #self.gridLayout_RunChanges.addWidget(self.lineEdit_Angle, row, column, 1, 5)
        #self.lineEdit_Angle.setText("angle")
        self.QSpinBox_angle = QtWidgets.QSpinBox(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.QSpinBox_angle, row, column, 1, 1)
        self.QSpinBox_angle.setRange(-90, 90)
        self.QSpinBox_angle.setValue(self.current_angle)
        self.QSpinBox_angle.valueChanged.connect(self.angleChange)
        self.QSpinBox_angle.setEnabled(False)
        columnWids.append(self.QSpinBox_angle)

        self.pushButton_updateAngle = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_updateAngle, row, column, 1, 2)
        self.pushButton_updateAngle.setText("Update Angle")
        self.pushButton_updateAngle.clicked.connect(self.updateAngle)
        self.pushButton_updateAngle.setEnabled(False)
        columnWids.append(self.pushButton_updateAngle)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

        row += 1
        self.label_chip_no = QtWidgets.QLabel()
        # self.gridLayout_RunChanges.addWidget(self.label_chip_no, row, column, 1, 2)
        self.label_chip_no.setText("Crystal Type")
        columnWids.append(self.label_chip_no)

        self.comboBox_Crystal = QtWidgets.QComboBox(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.lineEdit_Crystal, row, column, 1, 5)
        self.comboBox_Crystal.addItem("PbF2_6mm")
        self.comboBox_Crystal.addItem("BGO_6mm")
        self.comboBox_Crystal.addItem("PWO_6mm")
        self.comboBox_Crystal.addItem("DSB-3")
        self.comboBox_Crystal.addItem("ABSZL")
        self.comboBox_Crystal.addItem("ABSC5")
        self.comboBox_Crystal.addItem("BGO_18mm")
        self.comboBox_Crystal.addItem("PWO_20mm")
        self.comboBox_Crystal.addItem("SICBSO1309")
        # self.lineEdit_chip_no.editingFinished.connect(self.make_new_folder)
        columnWids.append(self.comboBox_Crystal)


        self.label_sipm_type_A = QtWidgets.QLabel()
        self.label_sipm_type_A.setText("SiPM_A")
        columnWids.append(self.label_sipm_type_A)
        self.comboBox_SiPMtypeA = QtWidgets.QComboBox(self.gridLayoutWidget_RunChanges)
        self.comboBox_SiPMtypeA.addItem("Ha")
        self.comboBox_SiPMtypeA.addItem("Br")
        columnWids.append(self.comboBox_SiPMtypeA)

        self.label_filter_type_A = QtWidgets.QLabel()
        self.label_filter_type_A.setText("filter_A")
        columnWids.append(self.label_filter_type_A)
        self.comboBox_filter_typeA = QtWidgets.QComboBox(self.gridLayoutWidget_RunChanges)
        self.comboBox_filter_typeA.addItem("No")
        self.comboBox_filter_typeA.addItem("U330")
        self.comboBox_filter_typeA.addItem("R64")
        columnWids.append(self.comboBox_filter_typeA)


        self.label_sipm_type_B = QtWidgets.QLabel()
        self.label_sipm_type_B.setText("SiPM_B")
        columnWids.append(self.label_sipm_type_B)
        self.comboBox_SiPMtypeB = QtWidgets.QComboBox(self.gridLayoutWidget_RunChanges)
        self.comboBox_SiPMtypeB.addItem("Ha")
        self.comboBox_SiPMtypeB.addItem("Br")
        columnWids.append(self.comboBox_SiPMtypeB)

        self.label_filter_type_B = QtWidgets.QLabel()
        self.label_filter_type_B.setText("filter_B")
        columnWids.append(self.label_filter_type_B)
        self.comboBox_filter_typeB = QtWidgets.QComboBox(self.gridLayoutWidget_RunChanges)
        self.comboBox_filter_typeB.addItem("No")
        self.comboBox_filter_typeB.addItem("U330")
        self.comboBox_filter_typeB.addItem("R64")
        columnWids.append(self.comboBox_filter_typeB)

        # setup Row
        column = 0
        step = (int)(columnMax / len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w, row, column, 1, step)
            column += step
        
        columnWids = []

        row += 2
        columnWids.append(self.enableControlsUI())

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 3, step)
            column += step
        
        columnWids = []

        row += 3
        column = 0
        self.label_chip_no = QtWidgets.QLabel()
        # self.gridLayout_RunChanges.addWidget(self.label_chip_no, row, column, 1, 2)
        self.label_chip_no.setText("Start and Stop Controls")
        columnWids.append(self.label_chip_no)

        column += 2
        #self.pushButton_s = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        #self.gridLayout_RunChanges.addWidget(self.pushButton_s, row, column, 1, 1)
        #self.pushButton_s.setText("Start/Stop acquisition")
        #self.pushButton_s.clicked.connect(lambda: self.sendChar("STARTSTOP"))

        self.checkBox_s = QtWidgets.QCheckBox(self.gridLayoutWidget_RunChanges)
        self.checkBox_s.setText("Start/Stop acquisition")
        # self.gridLayout_RunChanges.addWidget(self.checkBox_s, row, column, 1, 2)
        self.checkBox_s.setCheckState(bool(self.valueDict["STARTSTOP"]))
        self.checkBox_s.stateChanged.connect(lambda: self.enDisCheckBox("STARTSTOP"))
        columnWids.append(self.checkBox_s)


        column += 2
        self.pushButton_t = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_t, row, column, 1, 3)
        self.pushButton_t.setText("Send a software trigger (single shot)")
        self.pushButton_t.clicked.connect(lambda: self.sendChar("TRIGGER"))
        columnWids.append(self.pushButton_t)


        column += 3
        #self.pushButton_capT = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        #self.gridLayout_RunChanges.addWidget(self.pushButton_capT, row, column, 1, 1)
        #self.pushButton_capT.setText("Enable/Disable continuous software trigger")
        #self.pushButton_capT.clicked.connect(lambda: self.sendChar("ENTRIGGER"))

        self.checkBox_capT = QtWidgets.QCheckBox(self.gridLayoutWidget_RunChanges)
        self.checkBox_capT.setText("Continuous software trigger")
        # self.gridLayout_RunChanges.addWidget(self.checkBox_capT, row, column, 1, 2)
        self.checkBox_capT.setCheckState(bool(self.valueDict["ENTRIGGER"]))
        self.checkBox_capT.stateChanged.connect(lambda: self.enDisCheckBox("ENTRIGGER"))
        columnWids.append(self.checkBox_capT)

        # row += 1
        # column = 0
        # self.label_chip_no = QtWidgets.QLabel()
        # self.gridLayout_RunChanges.addWidget(self.label_chip_no, row, column, 1, 2)
        # self.label_chip_no.setText("Output Files")
        #
        # column += 2
        # self.pushButton_w = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_w, row, column, 1, 2)
        # self.pushButton_w.setText("Write one event to output file")
        # self.pushButton_w.clicked.connect(lambda: self.sendChar("WRITEFILE"))
        #
        # column += 2
        # #self.pushButton_capW = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # #self.gridLayout_RunChanges.addWidget(self.pushButton_capW, row, column, 1, 1)
        # #self.pushButton_capW.setText("Enable/Disable continuous writing to output file")
        # #self.pushButton_capW.clicked.connect(lambda: self.sendChar("CONTWRITEFILE"))
        #
        # self.checkBox_capW = QtWidgets.QCheckBox(self.gridLayoutWidget_RunChanges)
        # self.checkBox_capW.setText("Continuous writing to output file")
        # self.gridLayout_RunChanges.addWidget(self.checkBox_capW, row, column, 1, 3)
        # self.checkBox_capW.setCheckState(bool(self.valueDict["CONTWRITEFILE"]))
        # self.checkBox_capW.stateChanged.connect(lambda: self.enDisCheckBox("CONTWRITEFILE"))

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

        row += 1
        column = 0
        self.label_chip_no = QtWidgets.QLabel()
        # self.gridLayout_RunChanges.addWidget(self.label_chip_no, row, column, 1, 2)
        self.label_chip_no.setText("Plots")
        columnWids.append(self.label_chip_no)

        self.pushButton_p = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_p, row, column, 1, 2)
        self.pushButton_p.setText("Plot one event")
        self.pushButton_p.clicked.connect(lambda: self.sendChar("PLOTEVENT"))
        columnWids.append(self.pushButton_p)

        #self.pushButton_capP = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        #self.gridLayout_RunChanges.addWidget(self.pushButton_capP, row, column, 1, 1)
        #self.pushButton_capP.setText("Enable/Disable continuous plot")
        #self.pushButton_capP.clicked.connect(lambda: self.sendChar("CONTPLOTEVENT"))

        self.checkBox_capP = QtWidgets.QCheckBox(self.gridLayoutWidget_RunChanges)
        self.checkBox_capP.setText("Continuous plot")
        # self.gridLayout_RunChanges.addWidget(self.checkBox_capP, row, column, 1, 2)
        self.checkBox_capP.setCheckState(bool(self.valueDict["CONTPLOTEVENT"]))
        self.checkBox_capP.stateChanged.connect(lambda: self.enDisCheckBox("CONTPLOTEVENT"))
        columnWids.append(self.checkBox_capP)

        self.checkBox_GrpChange = QtWidgets.QCheckBox(self.gridLayoutWidget_RunChanges)
        self.checkBox_GrpChange.setText("Group 0/1")
        # self.gridLayout_RunChanges.addWidget(self.checkBox_GrpChange, row, column, 1, 2)
        self.checkBox_GrpChange.setCheckState(bool(self.valueDict["NEXTGRPEN"]))
        self.checkBox_GrpChange.stateChanged.connect(lambda: self.enDisCheckBox("NEXTGRPEN"))
        columnWids.append(self.checkBox_GrpChange)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

        row += 1
        column = 0
        row += 1
        column = 0
        self.label_chip_no = QtWidgets.QLabel()
        # self.gridLayout_RunChanges.addWidget(self.label_chip_no, row, column, 1, 2)
        self.label_chip_no.setText("Current Run")
        columnWids.append(self.label_chip_no)

        column += 2
        self.QSpinBox_runNum = QtWidgets.QSpinBox(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.QSpinBox_runNum, row, column, 1, 2)
        self.QSpinBox_runNum.setRange(0, 500)
        self.QSpinBox_runNum.setValue(self.current_run)
        #self.QSpinBox_runNum.valueChanged.connect(self.saveCurrentRun)
        columnWids.append(self.QSpinBox_runNum)

        column += 2
        self.pushButton_setNewRun = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_setNewRun, row, column, 1, 4)
        self.pushButton_setNewRun.setText("Change Run *Only if you made a mistake")
        self.pushButton_setNewRun.clicked.connect(self.setCurrentRun)
        self.pushButton_setNewRun.setEnabled(True)
        columnWids.append(self.pushButton_setNewRun)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

        row += 1
        column = 0
        self.pushButton_START = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_START, row, column, 2, 8)
        self.pushButton_START.setText("START")
        self.pushButton_START.clicked.connect(self.startEverything)
        self.pushButton_START.setEnabled(False)
        columnWids.append(self.pushButton_START)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step
        
        columnWids = []

        row += 2
        column = 0
        self.pushButton_STOP = QtWidgets.QPushButton(self.gridLayoutWidget_RunChanges)
        # self.gridLayout_RunChanges.addWidget(self.pushButton_STOP, row, column, 2, 8)
        self.pushButton_STOP.setText("STOP")
        self.pushButton_STOP.clicked.connect(self.stopEverything)
        self.pushButton_STOP.setEnabled(False)

        columnWids.append(self.pushButton_STOP)

        #setup Row
        column = 0
        step = (int)(columnMax/len(columnWids))
        for w in columnWids:
            self.gridLayout_RunChanges.addWidget(w,row,column, 1, step)
            column += step


    def enableControlsUI(self):
        self.deviceEnableControlRows = []
        self.gridLayoutWidget_CHNLENCTRL = QtWidgets.QWidget(self.gridLayoutWidget_RunChanges)
        self.gridLayout_CHNLENCTRL = QtWidgets.QGridLayout(self.gridLayoutWidget_CHNLENCTRL)

        row = 0
        column = 0
        self.label_channelEn = QtWidgets.QLabel()
        self.gridLayout_CHNLENCTRL.addWidget(self.label_channelEn, row, column, 3, 1)
        self.label_channelEn.setText("Channel Enables")
        column += 1

        self.pushButton_ChEN = QtWidgets.QPushButton(self.gridLayoutWidget_CHNLENCTRL)
        self.gridLayout_CHNLENCTRL.addWidget(self.pushButton_ChEN, row, column, 3, 1)
        self.pushButton_ChEN.setText("Update")
        self.pushButton_ChEN.clicked.connect(self.chEnCheckBox)

        gridLayoutWidget_scrolls = QtWidgets.QWidget(self.gridLayoutWidget_RunChanges)
        mygroupbox = QtWidgets.QGroupBox('Plot enables for each device')
        self.deviceScrollForm = QtWidgets.QFormLayout()
        column += 1
        for device in range(self.numDevices):
            self.deviceEnableControlRows.append(self.chnlEnRow(device))
            self.deviceScrollForm.addRow("Device %i" %device, self.deviceEnableControlRows[device])

        mygroupbox.setLayout(self.deviceScrollForm)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(mygroupbox)
        scroll.setWidgetResizable(True)

        self.gridLayout_CHNLENCTRL.addWidget(scroll, row, column, 3, 1)
        return self.gridLayoutWidget_CHNLENCTRL
    
    def chnlEnRow(self, device):
        widget = QtWidgets.QWidget(self.gridLayoutWidget_CHNLENCTRL)
        layout = QtWidgets.QGridLayout(widget)

        for i in range(8):
            label = QtWidgets.QLabel()
            layout.addWidget(label, 1, i, 1, 1)
            label.setText("ch_"+str(7-i))

            checkbox = QtWidgets.QCheckBox()
            layout.addWidget(checkbox, 1, i, 1, 1)
            # if self.deviceValueDic[device]["SETCHANNELEN"][i] == '1':
            #     checkbox.setChecked(True)
            self.deviceCheckBoxList[device].append(checkbox)
        
        return widget

    def closeReviewHist(self):
        self.pushButton_closePastHist.setEnabled(False)
        del self.reviewDecode

    def setupROOTHistoryUI(self):
        self.gridLayoutWidget_RootHist = QtWidgets.QWidget(self.centralwidget)
        self.gridLayout_RootHist = QtWidgets.QGridLayout(self.gridLayoutWidget_RootHist)
        
        row = 0
        column = 0
        self.comboBox_pastGraphs = QtWidgets.QComboBox(self.gridLayoutWidget_RootHist)
        self.gridLayout_RootHist.addWidget(self.comboBox_pastGraphs, row, column, 1, 3)
        self.comboBox_pastGraphs.setAccessibleName('Past_Graphs')
        self.comboBox_pastGraphs.addItems(self.root_files)
        self.comboBox_pastGraphs.setCurrentIndex(0)
        #self.comboBox_pastGraphs.currentIndexChanged.connect(self.setTriggerTR0)

        column = 3
        self.pushButton_seePastHist = QtWidgets.QPushButton(self.gridLayoutWidget_RootHist)
        self.gridLayout_RootHist.addWidget(self.pushButton_seePastHist, row, column, 1, 2)
        self.pushButton_seePastHist.setText("Review Histogram")
        self.pushButton_seePastHist.clicked.connect(self.reviewHist)

        row += 2
        column = 0
        self.pushButton_refreshPastHist = QtWidgets.QPushButton(self.gridLayoutWidget_RootHist)
        self.gridLayout_RootHist.addWidget(self.pushButton_refreshPastHist, row, column, 1, 2)
        self.pushButton_refreshPastHist.setText("Refresh Root Files List")
        self.pushButton_refreshPastHist.clicked.connect(self.updateHistList)

        column = 3
        self.pushButton_closePastHist = QtWidgets.QPushButton(self.gridLayoutWidget_RootHist)
        self.gridLayout_RootHist.addWidget(self.pushButton_closePastHist, row, column, 1, 2)
        self.pushButton_closePastHist.setText("Close Review Histogram")
        self.pushButton_closePastHist.clicked.connect(self.closeReviewHist)
        self.pushButton_closePastHist.setEnabled(False)

        

    def setupImportantMessageUI(self):
        self.verticalLayoutWidget_ImptMess = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_ImptMess.setGeometry(QtCore.QRect(10, 530, 1180, 100))
        self.verticalLayout_ImptMess = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_ImptMess)
        self.verticalLayout_ImptMess.setContentsMargins(0, 0, 0, 0)

        self.label_ImptMess = QtWidgets.QLabel(self.verticalLayoutWidget_ImptMess)
        self.verticalLayout_ImptMess.addWidget(self.label_ImptMess)
        self.label_ImptMess.setText("")
        self.label_ImptMess.setStyleSheet("color : red")
        

    def setupConfiguTabsUI(self):
        self.deviceConfigTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        #self.tab_digitizer_config = tab_digitizer_config(self.deviceConfigTabWidget)
        #self.deviceConfigTabWidget.setGeometry(QtCore.QRect(10,0,880,350))
        for i, name in enumerate(["High Gain", "Low Gain"]):
            self.deviceConfigTabs.append(self.setupConfigureUI(i))
            # self.deviceConfigTabs.append(self.tab_digitizer_config.setupConfigureUI(i))
            self.deviceConfigTabWidget.addTab(self.deviceConfigTabs[i], name)

    def setupUi(self, MainWindow):
        self.findCurrentAngle()
        self.findCurrentRun()
        self.rootFileSearch()
        self.setupForDeviceNum()

        MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1200, 900)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # self.centralwidget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        MainWindow.setWindowTitle("Wave Dump DESY")
        MainWindow.setCentralWidget(self.centralwidget)
        
        mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        mainLayout.addWidget(self.tabWidget)
        # self.tabWidget.setGeometry(QtCore.QRect(10,0,1180,600))
        # MainWindow.setCentralWidget(self.tabWidget)

        #self.setupConfigureUI()
        self.generalSettingsUI()
        #Stuff to change during run!
        self.setupRunUI()
        self.setupROOTHistoryUI()
        self.setupConfiguTabsUI()

        
        self.setupImportantMessageUI()

        # self.verticalLayoutWidget_TextBrowser = QtWidgets.QWidget(self.centralwidget)
        # self.verticalLayoutWidget_TextBrowser.setGeometry(QtCore.QRect(20, 640, 1160, 240))
        # self.verticalLayout_TextBrowser = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_TextBrowser)
        # self.verticalLayout_TextBrowser.setContentsMargins(0, 0, 0, 0)
        # self.label_TextBrowser = QtWidgets.QLabel(self.verticalLayoutWidget_TextBrowser)
        # self.label_TextBrowser.setText("Output log")
        # self.verticalLayout_TextBrowser.addWidget(self.label_TextBrowser)
        # #general textbrowser
        # self.textBrowser = QtWidgets.QTextBrowser(self.verticalLayoutWidget_TextBrowser)
        # self.verticalLayout_TextBrowser.addWidget(self.textBrowser)

        self.label_TextBrowser = QtWidgets.QLabel()
        self.label_TextBrowser.setText("Output log")
        self.label_TextBrowser.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        mainLayout.addWidget(self.label_TextBrowser)

        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setMinimumHeight(100)
        self.textBrowser.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        mainLayout.addWidget(self.textBrowser)

        #tabs
        self.tabWidget.addTab(self.gridLayoutWidget_RunChanges, "Run Settings")
        self.tabWidget.addTab(self.deviceConfigTabWidget, "Devices Configure")
        self.tabWidget.addTab(self.gridLayoutWidget_RootHist, "Root History")
        self.tabWidget.addTab(self.gridLayoutWidget_generalSettings, "General Settings")

        self.tab_SiPM_HV_config = QtWidgets.QWidget(self.centralwidget)
        self.tabWidget.addTab(self.tab_SiPM_HV_config,"SiPM HV control")
        self.tab_SiPM_HV_config_ins = tab_SiPM_HV_config(self.tab_SiPM_HV_config,self.portsList)

        self.tab_PIcontrol = QtWidgets.QWidget(self.centralwidget)
        self.tabWidget.addTab(self.tab_PIcontrol,"PI control")
        self.tab_PIcontrol_inst = tab_PIcontrol(self.tab_PIcontrol)

        self.tab_DAQ_control = QtWidgets.QWidget(self.centralwidget)
        self.tabWidget.addTab(self.tab_DAQ_control,"DAQ control")
        self.tab_DAQ_control_inst = tab_DAQ_control(self.tab_DAQ_control)

        self.tab_calibrate = QtWidgets.QWidget(self.centralwidget)
        self.tabWidget.addTab(self.tab_calibrate, "Calibration")
        self.tab_calibrate_inst = tab_calibrate(self.tab_calibrate)

    def start_WaveDump(self):
        # Step 2: Create a QThread object
        self.pushButton_startWD.setEnabled(False)
        self.emptyFile()
        files = self.writeConfigFile()
        self.chEnCheckBox()
        self.WDstarted = True
        print('debug')
        self.thread_startWD = QThread()
        # Step 3: Create a worker_startWD object
        self.worker_startWD = Worker_startWaveDump()
        for file in files:
            self.worker_startWD.arrCall.append(file)
        # print(self.worker_startWD.arrCall)
        # Step 4: Move worker_startWD to the thread
        self.worker_startWD.moveToThread(self.thread_startWD)
        # Step 5: Connect signals and slots
        self.thread_startWD.started.connect(self.worker_startWD.run)
        self.worker_startWD.finished.connect(self.thread_startWD.quit)
        self.worker_startWD.finished.connect(self.worker_startWD.deleteLater)
        # self.worker_startWD.finished.connect(self.WDQuit)
        self.thread_startWD.finished.connect(self.thread_startWD.deleteLater)
        # Step 6: Start the thread
        self.thread_startWD.start()
        
        self.thread_startWD.finished.connect(
            lambda: self.pushButton_START.setEnabled(True))
        # self.pushButton_START.setEnabled(False)
        # time.sleep(3000)
        # self.pushButton_START.setEnabled(True)

    def run_externalDecode(self):
        # Step 2: Create a QThread object
        self.thread_ExDecode = QThread()
        # Step 3: Create a worker_startWD object
        self.worker_runDecode = Worker_runDecode(self.file_name, str(self.numDevices))
        # Step 4: Move worker_startWD to the thread
        self.worker_runDecode.moveToThread(self.thread_ExDecode)
        # Step 5: Connect signals and slots
        self.thread_ExDecode.started.connect(self.worker_runDecode.run)
        self.worker_runDecode.finished.connect(self.thread_ExDecode.quit)
        self.worker_runDecode.finished.connect(self.worker_runDecode.deleteLater)
        self.thread_ExDecode.finished.connect(self.thread_ExDecode.deleteLater)
        # Step 6: Start the thread
        self.thread_ExDecode.start()
        # self.pushButton_START.setEnabled(False)
        # time.sleep(3000)
        # self.pushButton_START.setEnabled(True)
        
    def start_Decode(self):
        # Step 2: Create a QThread object
        chnl_names = []
        for n in range(self.numDevices):
            chnl_names.append([])
            if self.chnl_controls[n][0].currentText() == "YES":
                chnl_names[n] += ['00', '01', '02', '03', '04', '05', '06', '07', 'TR_0_0']
            if self.chnl_controls[n][1].currentText() == "YES":
                chnl_names[n] += ['08', '09', '10', '11', '12', '13', '14', '15']
        print(chnl_names)
        print('starting python decode')
        self.threadDecode = QThread()
        # Step 3: Create a worker_startWD object
        self.worker_startDec = Worker_startDecode(self.file_name, str(self.numDevices), chnl_names)
        # Step 4: Move worker_startWD to the thread
        self.worker_startDec.moveToThread(self.threadDecode)
        # Step 5: Connect signals and slots
        self.threadDecode.started.connect(self.worker_startDec.run)
        self.worker_startDec.finished.connect(self.threadDecode.quit)
        self.worker_startDec.finished.connect(self.worker_startDec.deleteLater)
        self.threadDecode.finished.connect(self.threadDecode.deleteLater)

        # Step 6: Start the thread
        self.threadDecode.start()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_MainWindow()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
