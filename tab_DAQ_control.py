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








class tab_DAQ_control(object):

    def __init__(self, MainWindow):
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
        self.pushButton_startDAQ = QtWidgets.QPushButton()
        self.pushButton_startDAQ.setText("Start DAQ")
        self.buttonLayout.addWidget(self.pushButton_startDAQ, 0, column, 1, 1)
        self.pushButton_startDAQ.clicked.connect(self.start_DAQ)


        column += 1
        self.pushButton_stopDAQ = QtWidgets.QPushButton()
        self.pushButton_stopDAQ.setText("Stop DAQ")
        self.buttonLayout.addWidget(self.pushButton_stopDAQ, 0, column, 1, 1)
        self.pushButton_stopDAQ.clicked.connect(self.stop_DAQ)
        self.pushButton_stopDAQ.setEnabled(False)


        column += 1
        self.pushButton_single_plot = QtWidgets.QPushButton()
        self.pushButton_single_plot.setText("Single plot")
        self.buttonLayout.addWidget(self.pushButton_single_plot, 0, column, 1, 1)
        self.pushButton_single_plot.clicked.connect(self.single_plot)
        self.pushButton_single_plot.setEnabled(False)

        column += 1
        self.checkBox_cont_plot = QtWidgets.QPushButton()
        self.checkBox_cont_plot.setText("Continuous plot")
        self.checkBox_cont_plot.setCheckable(True)
        self.checkBox_cont_plot.setChecked(False)
        self.checkBox_cont_plot.setEnabled(False)
        self.buttonLayout.addWidget(self.checkBox_cont_plot, 0, column, 1, 1)
        self.cont_timer = QtCore.QTimer()
        self.cont_timer.setInterval(1000)
        self.cont_timer.timeout.connect(self.cont_plot)
        self.checkBox_cont_plot.toggled.connect(
            lambda: self.cont_timer.start() if self.checkBox_cont_plot.isChecked() else self.cont_timer.stop())

        column += 1
        self.pushButton_resetDAQ = QtWidgets.QPushButton()
        self.pushButton_resetDAQ.setText("Reset DAQs")
        self.buttonLayout.addWidget(self.pushButton_resetDAQ, 0, column, 1, 1)
        self.pushButton_resetDAQ.clicked.connect(Reset_DAQ.execute)

        
        self.sectionLayout.addWidget(self.buttonWindow)

        self.plotWindow = QtWidgets.QWidget()
        self.plotWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.sectionLayout.addWidget(self.plotWindow)
        self.setup_UI_waveform_plot()



    def setup_UI_waveform_plot(self):

        pg.setConfigOptions(antialias=True)        

        self.plotLayout = QtWidgets.QHBoxLayout(self.plotWindow)

        self.hgGridLayout = pg.GraphicsLayoutWidget()
        self.hgGridLayout.setBackground('w')
        self.plotLayout.addWidget(self.hgGridLayout)

        self.hg_plot_graph = self.hgGridLayout.addPlot(title="HG_Waveform")
        hg_legend = pg.LegendItem(horSpacing=0, frame=False, colCount=1)
        self.hgGridLayout.addItem(hg_legend)

        self.hg_plot_graph.setTitle("HG Waveform", color="b", size="10pt")
        styles = {"color": "red", "font-size": "12px"}
        self.hg_plot_graph.setLabel("left", "Channel [mV]", **styles)
        self.hg_plot_graph.setLabel("bottom", "Time [ns]", **styles)
        self.hg_plot_graph.showGrid(x=True, y=True)

        self.hg_plots = [self.hg_plot_graph.plot([0], [0], pen = pg.intColor(i), name="HG Channel {}".format(i)) for i in range(8)]
        for i in range(len(self.hg_plots)):
            hg_legend.addItem(self.hg_plots[i], "HG Channel {}".format(i))
        

        self.lgGridLayout = pg.GraphicsLayoutWidget()
        self.lgGridLayout.setBackground('w')
        self.plotLayout.addWidget(self.lgGridLayout)
 
        self.lg_plot_graph = self.lgGridLayout.addPlot(title="LG_Waveform")
        lg_legend = pg.LegendItem(horSpacing=0, frame=False, colCount=1)
        self.lgGridLayout.addItem(lg_legend)

        self.lg_plot_graph.setTitle("LG Waveform", color="b", size="10pt")
        styles = {"color": "red", "font-size": "12px"}
        self.lg_plot_graph.setLabel("left", "Channel [mV]", **styles)
        self.lg_plot_graph.setLabel("bottom", "Time [ns]", **styles)
        self.lg_plot_graph.showGrid(x=True, y=True)

        self.lg_plots = [self.lg_plot_graph.plot([0], [0], pen = pg.intColor(i), name="LG Channel {}".format(i)) for i in range(8)]
        for i in range(len(self.lg_plots)):
            lg_legend.addItem(self.lg_plots[i], "LG Channel {}".format(i))
     

    def start_DAQ(self):
        # Step 2: Create a QThread object
        self.pushButton_startDAQ.setEnabled(False)
        self.pushButton_stopDAQ.setEnabled(True)
        self.pushButton_single_plot.setEnabled(True)
        self.checkBox_cont_plot.setEnabled(True)

        self.thread_startDAQ = QThread()
        # Step 3: Create a worker_startDAQ object
        self.worker_startDAQ = Worker_startDAQ()

        # Step 4: Move worker_startDAQ to the thread
        self.worker_startDAQ.moveToThread(self.thread_startDAQ)
        # Step 5: Connect signals and slots
        self.thread_startDAQ.started.connect(self.worker_startDAQ.run)
        self.worker_startDAQ.finished.connect(self.thread_startDAQ.quit)
        self.worker_startDAQ.finished.connect(self.worker_startDAQ.deleteLater)
        
        self.thread_startDAQ.finished.connect(self.thread_startDAQ.deleteLater)

        # self.worker_startDAQ.finished.connect(self.WDQuit)
        # self.thread_startDAQ.finished.connect(self.thread_startDAQ.deleteLater)
        # Step 6: Start the thread
        self.thread_startDAQ.start()
        
        self.thread_startDAQ.finished.connect(self.DAQ_stopped)

    def stop_DAQ(self):
        self.worker_startDAQ.stop()

    def DAQ_stopped(self):
        self.pushButton_startDAQ.setEnabled(True)
        self.pushButton_stopDAQ.setEnabled(False)
        self.pushButton_single_plot.setEnabled(False)
        self.checkBox_cont_plot.setEnabled(False)

    def single_plot(self):
        self.update_plot(self.worker_startDAQ.single_plot())

    def cont_plot(self):
        if self.checkBox_cont_plot.isEnabled():
            self.single_plot()
            
    def update_plot(self, waveform_data):  
        hg_times, hg_channels, lg_times, lg_channels = waveform_data
        for i in range(len(hg_channels)):
            self.hg_plots[i].setData(hg_times, hg_channels[i])
        
        for i in range(len(lg_channels)):
            self.lg_plots[i].setData(lg_times, lg_channels[i])
