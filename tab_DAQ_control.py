import socket
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import subprocess
import struct
import time
from Worker_startDAQ import *
import pandas as pd
import numpy as np
from MonitorPlots import *


class tab_DAQ_control(object):

    def __init__(self, run_config, status, MainWindow):
        self.run_config = run_config
        self.status = status
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        self.sectionLayout = QtWidgets.QVBoxLayout(MainWindow)
        self.sectionLayout.setSpacing(0)
        self.sectionLayout.setContentsMargins(0,0,0,0)
        MainWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        self.buttonWindow = QtWidgets.QWidget()
        self.buttonWindow.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.buttonLayout = QtWidgets.QGridLayout(self.buttonWindow)


        column = 0
        self.pushButton_single_plot = QtWidgets.QPushButton()
        self.pushButton_single_plot.setText("Single plot")
        self.buttonLayout.addWidget(self.pushButton_single_plot, 0, column, 1, 1)
        self.pushButton_single_plot.clicked.connect(self.single_plot)
        self.pushButton_single_plot.setEnabled(False)

        column += 1
        self.pushButton_resetDAQ = QtWidgets.QPushButton()
        self.pushButton_resetDAQ.setText("Reset DAQs")
        self.buttonLayout.addWidget(self.pushButton_resetDAQ, 0, column, 1, 1)
        self.pushButton_resetDAQ.clicked.connect(Reset_DAQ.execute)

        
        self.sectionLayout.addWidget(self.buttonWindow)

        self.monitor_plots = MonitorPlots(self.status)
        self.monitor_plots.make_waveform_plot('HG Waveform', 'HG Channel {}', 8)
        self.monitor_plots.make_waveform_plot('LG Waveform', 'LG Channel {}', 8)
        self.monitor_plots.request_monitor_data.connect(self.single_plot)
        self.sectionLayout.addWidget(self.monitor_plots.get_layout_widget())

    def start_DAQ(self):
        # Step 2: Create a QThread object
        self.pushButton_single_plot.setEnabled(True)

        self.thread_startDAQ = QThread()
        # Step 3: Create a worker_startDAQ object
        self.worker_startDAQ = Worker_startDAQ(self.run_config)

        # Step 4: Move worker_startDAQ to the thread
        self.worker_startDAQ.moveToThread(self.thread_startDAQ)

        # Step 5: Connect signals and slots
        self.thread_startDAQ.started.connect(self.worker_startDAQ.run)
        self.worker_startDAQ.finished.connect(self.thread_startDAQ.quit)
        self.worker_startDAQ.finished.connect(self.worker_startDAQ.deleteLater)
        
        self.thread_startDAQ.finished.connect(self.thread_startDAQ.deleteLater)

        # Step 6: Start the thread
        self.thread_startDAQ.start()
        
        self.thread_startDAQ.finished.connect(self.DAQ_stopped)

    def stop_DAQ(self):
        self.worker_startDAQ.stop()

    def DAQ_stopped(self):
        self.pushButton_single_plot.setEnabled(False)

    def single_plot(self):
        self.update_plot(self.worker_startDAQ.single_plot())

    def update_plot(self, waveform_data):  
        hg_times, hg_channels, lg_times, lg_channels = waveform_data
        if hg_times != None and hg_channels != None:
            for i in range(len(hg_channels)):
                self.hg_plots[i].setData(hg_times, hg_channels[i])
        
        if lg_times != None and lg_channels != None:
            for i in range(len(lg_channels)):
                self.lg_plots[i].setData(lg_times, lg_channels[i])
