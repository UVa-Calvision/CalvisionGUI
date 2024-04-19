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


class tab_DAQ_control(QtCore.QObject):

    daq_readout_stopped = QtCore.pyqtSignal()

    def __init__(self, run_config, status, MainWindow):
        super().__init__()
        self.run_config = run_config
        self.status = status
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        self.sectionLayout = QtWidgets.QVBoxLayout(MainWindow)
        self.sectionLayout.setSpacing(0)
        self.sectionLayout.setContentsMargins(0,0,0,0)
        MainWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        channelWindow = QtWidgets.QWidget()
        channelWindow.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        channelLayout = QtWidgets.QHBoxLayout(channelWindow)
        self.sectionLayout.addWidget(channelWindow)

        self.pushButton_single_plot = QtWidgets.QPushButton()
        self.pushButton_single_plot.setText("Single plot")
        self.pushButton_single_plot.clicked.connect(self.single_plot)
        self.pushButton_single_plot.setEnabled(False)
        self.pushButton_single_plot.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        channelLayout.addWidget(self.pushButton_single_plot)


        channelEnableWindow = QtWidgets.QWidget()
        enableLayout = QtWidgets.QGridLayout(channelEnableWindow)
        channelLayout.addWidget(channelEnableWindow)

        row = 0
        column = 0
        label = QtWidgets.QLabel()
        label.setText("View Channel")
        enableLayout.addWidget(label, row, column, 1, 1)
 
        for i in range(4):
            label = QtWidgets.QLabel()
            label.setText("Front {}".format(i))
            enableLayout.addWidget(label, row, column + 1 + i, 1, 1, QtCore.Qt.AlignHCenter)

        for i in range(4):
            label = QtWidgets.QLabel()
            label.setText("Rear {}".format(i))
            enableLayout.addWidget(label, row, column + 4 + 1 + i, 1, 1, QtCore.Qt.AlignHCenter)


        self.channel_enable_checkboxes = []

        row += 1
        label = QtWidgets.QLabel()
        label.setText("High Gain")
        enableLayout.addWidget(label, row, column, 1, 1)
        for i in range(8):
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(True)
            checkbox.clicked.connect(self.channel_enable_changed)
            enableLayout.addWidget(checkbox, row, column + 1 + i, 1, 1, QtCore.Qt.AlignHCenter)
            self.channel_enable_checkboxes.append(checkbox)

        row += 1
        label = QtWidgets.QLabel()
        label.setText("Low Gain")
        enableLayout.addWidget(label, row, column, 1, 1)
        for i in range(8):
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(True)
            checkbox.clicked.connect(self.channel_enable_changed)
            enableLayout.addWidget(checkbox, row, column + 1 + i, 1, 1, QtCore.Qt.AlignHCenter)
            self.channel_enable_checkboxes.append(checkbox)

        


        self.monitor_plots = MonitorPlots(self.status)
        self.monitor_plots.make_waveform_plot('HG Waveform', 'HG{}', 8)
        legend = pg.LegendItem(horSpacing = 0, frame = False, colCount = 1)
        for i in range(4):
            legend.addItem(self.monitor_plots.lines[i   ], 'FH{}'.format(i))
            legend.addItem(self.monitor_plots.lines[i+ 4], 'BH{}'.format(i))
        self.monitor_plots.layoutWidget.addItem(legend)

        self.monitor_plots.make_waveform_plot('LG Waveform', 'LG{}', 8)
        legend = pg.LegendItem(horSpacing = 0, frame = False, colCount = 1)
        for i in range(4):
            legend.addItem(self.monitor_plots.lines[i+ 8], 'FL{}'.format(i))
            legend.addItem(self.monitor_plots.lines[i+12], 'BL{}'.format(i))
        self.monitor_plots.layoutWidget.addItem(legend)

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
        
        # Step 6: Start the thread
        self.thread_startDAQ.start()
        
        self.thread_startDAQ.finished.connect(self.DAQ_stopped)

    def stop_DAQ(self):
        self.worker_startDAQ.stop()

    def DAQ_stopped(self):
        self.pushButton_single_plot.setEnabled(False)
        print("Emitting DAQ readout stopped")
        self.daq_readout_stopped.emit()

    def single_plot(self):
        self.update_plot(self.worker_startDAQ.single_plot())

    def channel_enable_changed(self):
        pass
        for i in range(16):
            self.monitor_plots.lines[i].setVisible(self.channel_enable_checkboxes[i].isChecked())

    def update_plot(self, waveform_data):  
        hg_times, hg_channels, lg_times, lg_channels = waveform_data
        if hg_times != None and hg_channels != None:
            for i in range(8):
                self.monitor_plots.set_data(i, hg_times, hg_channels[i])
        
        if lg_times != None and lg_channels != None:
            for i in range(8):
                self.monitor_plots.set_data(8+i, lg_times, lg_channels[i])
