from PyQt5 import QtGui, QtCore, QtWidgets
from tab_SiPM_HV_config import tab_SiPM_HV_config
from tab_PIcontrol import tab_PIcontrol
from tab_DAQ_control import tab_DAQ_control
from tab_calibrate import tab_calibrate
from tab_digitizer_config import tab_digitizer_config
from tab_run_control import tab_run_control
from tab_previous_runs import tab_previous_runs

from RunConfig import *
from DeviceList import *

class RunStatus:
    def __init__(self):
        self.monitor_time = 0
        self.is_running = False
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.timeout)
        self.update_timer.start()

    def timeout(self):
        self.monitor_time += self.update_timer.interval() / 1000

    def begin_run(self):
        is_running = True
        self.monitor_time = 0

    def end_run(self):
        is_running = False


class Ui_MainWindow():
    
    def __init__(self):
        self.run_config = RunConfig()
        self.status = RunStatus()
        self.device_list = DeviceList()

    def setupUi(self, MainWindow):
        
        MainWindow.setWindowTitle("Wave Dump DESY")
        
        # Setup main layout
        self.centralWidget = QtWidgets.QWidget()
        MainWindow.setCentralWidget(self.centralWidget)

        mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        mainLayout.addWidget(self.tabWidget)


        label_TextBrowser = QtWidgets.QLabel()
        label_TextBrowser.setText("Output Log")
        label_TextBrowser.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        mainLayout.addWidget(label_TextBrowser)
        
        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setMinimumHeight(100)
        self.textBrowser.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        mainLayout.addWidget(self.textBrowser)

        # Setup tabs
        run_control_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(run_control_tab, "Run Control")
        self.tab_run_control_inst = tab_run_control(self.run_config, run_control_tab)

        previous_runs_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(previous_runs_tab, "Previous Runs")
        self.tab_previous_runs_inst = tab_previous_runs(previous_runs_tab)

        digi_config_tab = QtWidgets.QTabWidget()
        self.tabWidget.addTab(digi_config_tab, "Digitizer Configuration")
        self.tab_digi_config_insts = []
        for i, name in enumerate(["High Gain", "Low Gain"]):
            digi_device_config_tab = QtWidgets.QWidget()
            self.tab_digi_config_insts.append(tab_digitizer_config(self.run_config, digi_device_config_tab))
            digi_config_tab.addTab(digi_device_config_tab, name)

        sipm_hv_config_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(sipm_hv_config_tab, "SiPM HV Control")
        self.tab_sipm_hv_config_inst = tab_SiPM_HV_config(self.run_config, self.status, sipm_hv_config_tab, self.device_list)

        pi_control_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(pi_control_tab, "PI Control")
        self.tab_pi_control_inst = tab_PIcontrol(self.run_config, self.status, pi_control_tab)

        daq_control_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(daq_control_tab, "DAQ Control")
        self.tab_daq_control_inst = tab_DAQ_control(self.run_config, self.status, daq_control_tab)

        calibrate_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(calibrate_tab, "Calibrate")
        self.tab_calibrate_inst = tab_calibrate(calibrate_tab)

        
        # Connect signals - slots
        self.tab_run_control_inst.run_config_changed.connect(self.check_repeat)
        self.tab_run_control_inst.begin_run.connect(self.begin_run)
        self.tab_run_control_inst.end_run.connect(self.end_run)

        self.status.update_timer.timeout.connect(self.tab_pi_control_inst.monitor_plots.monitor_callback)
        self.status.update_timer.timeout.connect(self.tab_sipm_hv_config_inst.monitor_plots.monitor_callback)
        self.status.update_timer.timeout.connect(self.tab_daq_control_inst.monitor_plots.monitor_callback)

        # Make sure state is up to date
        self.check_repeat()


    def check_repeat(self):
        self.tab_previous_runs_inst.update_run_table()
        exists = self.tab_previous_runs_inst.config_exists(self.run_config.to_dict())
        self.tab_run_control_inst.update_repeat_warning(exists)

    def begin_run(self):
        self.run_config.make_next_run()
        print("Starting next run: {}".format(self.run_config.run_number))
        self.tab_digi_config_insts[0].write_config(self.run_config.hg_config_file())
        self.tab_digi_config_insts[1].write_config(self.run_config.lg_config_file())
        self.status.begin_run()
        self.tab_daq_control_inst.monitor_plots.run_start()
        # self.tab_pi_control_inst.monitor_plots.run_start()
        self.tab_sipm_hv_config_inst.monitor_plots.run_start()
        self.tab_daq_control_inst.start_DAQ()

    def end_run(self):
        self.tab_daq_control_inst.stop_DAQ()
        self.status.end_run()
        self.tab_daq_control_inst.monitor_plots.run_stop()
        self.tab_pi_control_inst.monitor_plots.run_stop()
        self.tab_sipm_hv_config_inst.monitor_plots.run_stop()
        self.check_repeat()
