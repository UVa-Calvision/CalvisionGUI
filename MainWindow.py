from PyQt5 import QtGui, QtCore, QtWidgets
from tab_SiPM_HV_config import tab_SiPM_HV_config
from tab_PIcontrol import tab_PIcontrol
from tab_DAQ_control import tab_DAQ_control
from tab_calibrate import tab_calibrate
from tab_digitizer_config import tab_digitizer_config
from tab_run_control import tab_run_control
from tab_previous_runs import tab_previous_runs


class Ui_MainWindow():
    
    def __init__(self):
        pass

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
        self.tab_run_control_inst = tab_run_control(run_control_tab)

        previous_runs_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(previous_runs_tab, "Previous Runs")
        self.tab_previous_runs_inst = tab_previous_runs(previous_runs_tab)

        digi_config_tab = QtWidgets.QTabWidget()
        self.tabWidget.addTab(digi_config_tab, "Digitizer Configuration")
        self.tab_digi_config_insts = []
        for i, name in enumerate(["High Gain", "Low Gain"]):
            digi_device_config_tab = QtWidgets.QWidget()
            self.tab_digi_config_insts.append(tab_digitizer_config(digi_device_config_tab))
            digi_config_tab.addTab(digi_device_config_tab, name)

        sipm_hv_config_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(sipm_hv_config_tab, "SiPM HV Control")
        self.tab_sipm_hv_config_inst = tab_SiPM_HV_config(sipm_hv_config_tab, [])

        pi_control_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(pi_control_tab, "PI Control")
        self.tab_pi_control_inst = tab_PIcontrol(pi_control_tab)

        daq_control_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(daq_control_tab, "DAQ Control")
        self.tab_daq_control_inst = tab_DAQ_control(daq_control_tab)

        calibrate_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(calibrate_tab, "Calibrate")
        self.tab_calibrate_inst = tab_calibrate(calibrate_tab)

        
        # Connect signals - slots
        self.tab_run_control_inst.request_check_repeat.connect(self.check_repeat)
        self.check_repeat()

    def check_repeat(self):
        current_config = list(self.tab_run_control_inst.current_config_dict().values())
        self.tab_previous_runs_inst.update_run_table()
        exists = self.tab_previous_runs_inst.config_exists(current_config)
        self.tab_run_control_inst.update_repeat_warning(exists)
