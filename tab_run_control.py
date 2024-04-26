from PyQt5 import QtWidgets, QtCore
from RunConfig import *
# from CallProcess import *
import datetime

# class InhibitProcess(CallProcess):
#     def __init__(self):
#         pass
# 
#     def handle_output(self, line):
#         print(line)
# 
#     def execute(on):
#         postfix = "on"
#         if not on:
#             postfix = "off"
#         return InhibitProcess().run("python3 /home/uva/local_install/python/Inhibit_{}.py".format(postfix))


class tab_run_control(QtCore.QObject):

    status_fields = [
        "Local Time",
        "Run Time",
        "Run Status",
        "Front SiPM HV Voltage",
        "Front SiPM HV Current",
        "Front SiPM Temperature",
        "Back SiPM HV Voltage",
        "Back SiPM HV Current",
        "Back SiPM Temperature",
        "Box Temperature",
        "Box Relative Humidity",
        "LED Voltage",
        "BJT Bias",
        "LED Pulser Enabled",
        "Holdoff Pulser Enabled",
    ]

    
    run_config_changed = QtCore.pyqtSignal()
    begin_run = QtCore.pyqtSignal()
    end_run = QtCore.pyqtSignal()

    def __init__(self, run_config, run_status, MainWindow):
        super().__init__()
        self.run_config = run_config
        self.run_status = run_status
        self.status_values = {}
        for s in tab_run_control.status_fields:
            self.status_values[s] = None

        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)

        runSectionLabel = QtWidgets.QLabel()
        runSectionLabel.setText("----- Run Control")
        sectionLayout.addWidget(runSectionLabel)

        runWindow = QtWidgets.QWidget()
        runLayout = QtWidgets.QFormLayout(runWindow)
        sectionLayout.addWidget(runWindow)

        self.config_comboBoxes = {}
        for key in config_options:
            if key == 'Angle':
                self.config_angleLabel = QtWidgets.QLabel()
                self.config_angleLabel.setText("No angle set")
                runLayout.addRow(key, self.config_angleLabel)
                continue
            self.config_comboBoxes[key] = QtWidgets.QComboBox()
            self.config_comboBoxes[key].addItems(config_options[key])
            self.config_comboBoxes[key].setEditable(True)
            self.config_comboBoxes[key].currentTextChanged.connect(self.run_config_changed)
            runLayout.addRow(key, self.config_comboBoxes[key])

        self.repeat_warning = QtWidgets.QLabel()
        runLayout.addRow(self.repeat_warning)


        statusSectionLabel = QtWidgets.QLabel()
        statusSectionLabel.setText("----- Run Status")
        sectionLayout.addWidget(statusSectionLabel)

        statusWindow = QtWidgets.QWidget()
        statusWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        statusLayout = QtWidgets.QFormLayout(statusWindow)
        sectionLayout.addWidget(statusWindow)


        self.statusLabels = {}
        for name in tab_run_control.status_fields:
            self.statusLabels[name] = QtWidgets.QLabel()
            statusLayout.addRow(name + ":", self.statusLabels[name])


        runButtonWindow = QtWidgets.QWidget()
        runButtonWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        runButtonLayout = QtWidgets.QHBoxLayout(runButtonWindow)
        sectionLayout.addWidget(runButtonWindow)

        self.beginRunButton = QtWidgets.QPushButton()
        self.beginRunButton.setText("Begin Run")
        self.beginRunButton.clicked.connect(self.begin_run)
        self.beginRunButton.setEnabled(True)
        runButtonLayout.addWidget(self.beginRunButton)

        self.endRunButton = QtWidgets.QPushButton()
        self.endRunButton.setText("End Run")
        self.endRunButton.clicked.connect(self.end_run)
        self.endRunButton.setEnabled(False)
        runButtonLayout.addWidget(self.endRunButton)
        

        self.inhibit_checkbox = QtWidgets.QCheckBox()
        self.inhibit_checkbox.setText("Disable DAQ")
        self.inhibit_checkbox.setChecked(False)
        self.inhibit_checkbox.setEnabled(False)
        runButtonLayout.addWidget(self.inhibit_checkbox)

        self.led_checkbox = QtWidgets.QCheckBox()
        self.led_checkbox.setText("Turn on LED")
        self.led_checkbox.setChecked(False)
        self.led_checkbox.setEnabled(False)
        runButtonLayout.addWidget(self.led_checkbox)
        
        # Connect signals and slots

        self.run_config_changed.connect(self.update_config)
        self.begin_run.connect(self.begin_run_button)
        self.end_run.connect(self.end_run_button)
        
        
        # Update state

        self.run_config_changed.emit()
        self.update_status_all()
        self.enable_holdoff_controls(False, False)
        self.enable_led_controls(False, False)


    def begin_run_button(self):
        self.beginRunButton.setEnabled(False)
        self.endRunButton.setEnabled(True)
        self.set_config_editable(False)

    def end_run_button(self):
        self.beginRunButton.setEnabled(True)
        self.endRunButton.setEnabled(False)
        self.set_config_editable(True)

    def set_config_editable(self, enable):
        for box in self.config_comboBoxes:
            self.config_comboBoxes[box].setEnabled(enable)
    
    def enable_holdoff_controls(self, opened, enable):
        self.inhibit_checkbox.setEnabled(opened)
        self.inhibit_checkbox.setChecked(enable)
        self.set_config_editable(not enable)

    def enable_led_controls(self, opened, enable):
        self.led_checkbox.setEnabled(opened)
        self.led_checkbox.setChecked(enable)

    def update_config(self):
        config_values = {}
        for key in self.config_comboBoxes:
            config_values[key] = self.config_comboBoxes[key].currentText()
        config_values['Angle'] = self.config_angleLabel.text()
        self.run_config.from_dict(config_values)

    def update_repeat_warning(self, is_repeated):
        if is_repeated:
            self.repeat_warning.setText("WARNING: Run config already exists in staging area")
            self.repeat_warning.setStyleSheet("QLabel { color : red; }")
        else:
            self.repeat_warning.setText("Run config doesn't exist in staging area yet.")
            self.repeat_warning.setStyleSheet("QLabel { color : black; }")

    def update_status_all(self):
        for key in tab_run_control.status_fields:
            self.update_status(key)

    def update_status(self, key):
        if self.status_values[key] != None:
            self.statusLabels[key].setText(self.status_values[key])

    def update_angle(self, angle):
        if angle == None:
            self.config_angleLabel.setText("No angle set")
        else:
            self.config_angleLabel.setText(str(angle))
        self.run_config_changed.emit()
