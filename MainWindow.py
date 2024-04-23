from PyQt5 import QtGui, QtCore, QtWidgets
from tab_SiPM_HV_config import tab_SiPM_HV_config
from tab_PIcontrol import tab_PIcontrol
from tab_DAQ_control import tab_DAQ_control
from tab_calibrate import tab_calibrate
from tab_digitizer_config import tab_digitizer_config
from tab_run_control import tab_run_control
from tab_previous_runs import tab_previous_runs
from tab_rotor_control import tab_rotor_control

from RunConfig import *
from DeviceList import *

from datetime import datetime

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
        self.is_running = True
        self.monitor_time = 0

    def end_run(self):
        self.is_running = False


class Ui_MainWindow():
    
    def __init__(self):
        self.run_config = RunConfig()
        self.status = RunStatus()
        self.device_list = DeviceList()

        self.last_bjt_bias = None
        self.last_led_voltage = None
        self.last_pulser_enabled = None
        self.last_inhibit = None

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
        self.tab_run_control_inst = tab_run_control(self.run_config, self.status, run_control_tab)

        previous_runs_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(previous_runs_tab, "Previous Runs")
        self.tab_previous_runs_inst = tab_previous_runs(previous_runs_tab)

        rotor_control_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(rotor_control_tab, "Rotor Control")
        self.tab_rotor_control_inst = tab_rotor_control(self.run_config, self.status, self.device_list, rotor_control_tab)

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
        
        self.status.update_timer.timeout.connect(self.update_status)
        self.status.update_timer.timeout.connect(self.tab_pi_control_inst.monitor_plots.monitor_callback)
        self.status.update_timer.timeout.connect(self.tab_sipm_hv_config_inst.monitor_plots.monitor_callback)
        self.status.update_timer.timeout.connect(self.tab_daq_control_inst.monitor_plots.monitor_callback)

        self.tab_daq_control_inst.daq_readout_stopped.connect(self.tab_run_control_inst.end_run)

        self.tab_pi_control_inst.low_voltage_set.connect(self.set_last_led_voltage)
        self.tab_pi_control_inst.high_voltage_set.connect(self.set_last_bjt_bias)

        self.tab_calibrate_inst.pulser_enabled.connect(self.set_last_pulser_enabled)
        self.tab_run_control_inst.inhibit_enable.connect(self.set_last_inhibit_enabled)
        
        self.tab_rotor_control_inst.angle_changed.connect(self.tab_run_control_inst.update_angle)

        # Make sure state is up to date
        self.check_repeat()
        self.update_status()
        self.tab_run_control_inst.update_angle(self.tab_rotor_control_inst.angle)

        latest_run = self.tab_previous_runs_inst.latest_run()
        if latest_run != None:
            print("Attempting to load HG digitizer config from run {}".format(latest_run.run_number))
            try:
                self.tab_digi_config_insts[0].load_config(latest_run.hg_config_file())
                print("Successfully loaded")
            except Exception as e:
                print("Failed to load config")

            print("Attempting to load LG digitizer config from run {}".format(latest_run.run_number))
            try:
                self.tab_digi_config_insts[1].load_config(latest_run.lg_config_file())
                print("Successfully loaded")
            except Exception as e:
                print("Failed to load config")

    def set_last_led_voltage(self, v):
        self.last_led_voltage = v

    def set_last_bjt_bias(self, v):
        self.last_bjt_bias = v

    def set_last_pulser_enabled(self, t):
        self.last_pulser_enabled = t

    def set_last_inhibit_enabled(self, t):
        self.last_inhibit_enabled = t
        
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
        self.tab_run_control_inst.update_status_all()
        self.tab_daq_control_inst.monitor_plots.run_start()
        self.tab_pi_control_inst.monitor_plots.run_start()
        self.tab_sipm_hv_config_inst.monitor_plots.run_start()
        self.tab_daq_control_inst.start_DAQ()

    def end_run(self):
        if self.status.is_running:
            self.tab_daq_control_inst.stop_DAQ()
            self.status.end_run()
            self.tab_daq_control_inst.monitor_plots.run_stop()
            self.tab_pi_control_inst.monitor_plots.run_stop()
            self.tab_sipm_hv_config_inst.monitor_plots.run_stop()
            self.check_repeat()

    def update_status(self):
        monitor_value_if_exists = lambda tab, i: tab.monitor_plots.y_values[i][-1] if len(tab.monitor_plots.y_values[i]) > 0 else "-"

        self.tab_run_control_inst.status_values['Local Time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seconds = int(self.status.monitor_time) % 60
        minutes = int(self.status.monitor_time / 60)
        self.tab_run_control_inst.status_values['Run Time'] = '{} minutes {} seconds'.format(minutes, seconds)
        if self.status.is_running:
            self.tab_run_control_inst.status_values['Run Status'] = 'Running'
        else:
            self.tab_run_control_inst.status_values['Run Status'] = 'Not running'

        if self.tab_sipm_hv_config_inst.hv.ser != None:
            self.tab_run_control_inst.status_values['Front SiPM HV Voltage'] = '{} V'.format(monitor_value_if_exists(self.tab_sipm_hv_config_inst, 0))
            self.tab_run_control_inst.status_values['Front SiPM HV Current'] = '{} mA'.format(monitor_value_if_exists(self.tab_sipm_hv_config_inst, 1))
        else:
            self.tab_run_control_inst.status_values['Front SiPM HV Voltage'] = "Device not enabled"
            self.tab_run_control_inst.status_values['Front SiPM HV Current'] = "Device not enabled"

        if self.tab_sipm_hv_config_inst.hv2.ser != None:
            self.tab_run_control_inst.status_values['Back SiPM HV Voltage'] = '{} V'.format(monitor_value_if_exists(self.tab_sipm_hv_config_inst, 2))
            self.tab_run_control_inst.status_values['Back SiPM HV Current'] = '{} mA'.format(monitor_value_if_exists(self.tab_sipm_hv_config_inst, 3))
        else:
            self.tab_run_control_inst.status_values['Back SiPM HV Voltage'] = "Device not enabled"
            self.tab_run_control_inst.status_values['Back SiPM HV Current'] = "Device not enabled"

        self.tab_run_control_inst.status_values['Front SiPM Temperature'] = '{} C'.format(monitor_value_if_exists(self.tab_pi_control_inst, 0))
        self.tab_run_control_inst.status_values[ 'Back SiPM Temperature'] = '{} C'.format(monitor_value_if_exists(self.tab_pi_control_inst, 1))
        self.tab_run_control_inst.status_values[       'Box Temperature'] = '{} C'.format(monitor_value_if_exists(self.tab_pi_control_inst, 2))
        self.tab_run_control_inst.status_values[ 'Box Relative Humidity'] = '{} %'.format(monitor_value_if_exists(self.tab_pi_control_inst, 3))

        if self.last_led_voltage == None:
            self.tab_run_control_inst.status_values['LED Voltage'] = 'No last set of LED voltage'
        else:
            self.tab_run_control_inst.status_values['LED Voltage'] = str(self.last_led_voltage)

        if self.tab_pi_control_inst.checkBox_LED_HV_enable.isChecked():
            if self.last_bjt_bias == None:
                self.tab_run_control_inst.status_values['BJT Bias'] = 'No last set of BJT bias'
            else:
                self.tab_run_control_inst.status_values['BJT Bias'] = str(self.last_bjt_bias)
        else:
            self.tab_run_control_inst.status_values['BJT Bias'] = 'Disabled'

        if self.last_pulser_enabled == None:
            self.tab_run_control_inst.status_values['Pulser Enabled'] = 'No last set of pulser'
        else:
            self.tab_run_control_inst.status_values['Pulser Enabled'] = str(self.last_pulser_enabled)

        if self.last_inhibit == None:
            self.tab_run_control_inst.status_values['Inhibit Enabled'] = 'No last set of pulser'
        else:
            self.tab_run_control_inst.status_values['Inhibit Enabled'] = str(self.last_inhibit_enabled)
        
        self.tab_run_control_inst.update_status_all()
