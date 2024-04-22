from PyQt5 import QtWidgets, QtCore
from RunConfig import *
import datetime
import json


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
        "Pulser Enabled",
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

        subWindow = QtWidgets.QWidget()
        subWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        subLayout = QtWidgets.QHBoxLayout(subWindow)
        subLayout.setSpacing(20)
        sectionLayout.addWidget(subWindow)


        statusWindow = QtWidgets.QWidget()
        statusWindow.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        statusLayout = QtWidgets.QFormLayout(statusWindow)
        statusLayout.setSpacing(8)
        statusLayout.setHorizontalSpacing(30)
        subLayout.addWidget(statusWindow)

        statusSectionLabel = QtWidgets.QLabel()
        statusSectionLabel.setText("Run Status")
        statusLayout.addRow(statusSectionLabel)
        statusLayout.setAlignment(statusSectionLabel, QtCore.Qt.AlignHCenter)

        self.statusLabels = {}
        for name in tab_run_control.status_fields:
            self.statusLabels[name] = QtWidgets.QLabel()
            statusLayout.addRow(name + ":", self.statusLabels[name])

        
        configWindow = QtWidgets.QWidget()
        configWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        configLayout = QtWidgets.QFormLayout(configWindow)
        subLayout.addWidget(configWindow)

        self.numEvents_spinbox = QtWidgets.QSpinBox()
        self.numEvents_spinbox.setRange(0, 50000)
        self.numEvents_spinbox.setValue(20000)
        self.numEvents_spinbox.setSpecialValueText("No max")
        self.numEvents_spinbox.valueChanged.connect(self.update_time)
        configLayout.addRow("Number of events to readout", self.numEvents_spinbox)

        self.estimatedTriggerRate_spinbox = QtWidgets.QDoubleSpinBox()
        self.estimatedTriggerRate_spinbox.setSuffix(' kHz')
        self.estimatedTriggerRate_spinbox.setRange(0, 5)
        self.estimatedTriggerRate_spinbox.setValue(1)
        self.estimatedTriggerRate_spinbox.setSpecialValueText("No trigger")
        self.estimatedTriggerRate_spinbox.valueChanged.connect(self.update_time)
        configLayout.addRow("Estimated trigger rate", self.estimatedTriggerRate_spinbox)
        
        self.estimatedTime_spinbox = QtWidgets.QDoubleSpinBox()
        self.estimatedTime_spinbox.setSuffix(' min')
        self.estimatedTime_spinbox.setDecimals(2)
        self.estimatedTime_spinbox.setValue(20000.0 / 1000.0 / 60.0)
        self.estimatedTime_spinbox.setEnabled(False)
        self.estimatedTime_spinbox.setSpecialValueText("Forever")
        # self.estimatedTime_spinbox.valueChanged.connect(self.update_num_events)
        configLayout.addRow("Estimated readout duration", self.estimatedTime_spinbox)

        self.loadDevices_button = QtWidgets.QPushButton()
        self.loadDevices_button.setText("Load All Devices")
        configLayout.addRow(self.loadDevices_button)

        self.powerDown_button = QtWidgets.QPushButton()
        self.powerDown_button.setText("Power Down All Devices")
        configLayout.addRow(self.powerDown_button)

        self.defaultDevices_button = QtWidgets.QPushButton()
        self.defaultDevices_button.setText("Set Device Defaults")
        configLayout.addRow(self.defaultDevices_button)


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

        # Connect signals and slots

        self.run_config_changed.connect(self.update_config)
        self.begin_run.connect(self.begin_run_button)
        self.end_run.connect(self.end_run_button)

        # Update state

        self.update_config()
        self.update_status_all()


    def begin_run_button(self):
        self.beginRunButton.setEnabled(False)
        self.endRunButton.setEnabled(True)
        for box in self.config_comboBoxes:
            self.config_comboBoxes[box].setEnabled(False)

    def end_run_button(self):
        self.beginRunButton.setEnabled(True)
        self.endRunButton.setEnabled(False)
        for box in self.config_comboBoxes:
            self.config_comboBoxes[box].setEnabled(True)

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

    def save_run_stats(self, filename):
        try:
            with open(filename, 'w') as out:
                out.write(json.dumps(self.status_values, indent=4))
        except Exception as e:
            print("Failed to write run stats to {}: {}".format(filename, e))

    def update_time(self):
        if self.numEvents_spinbox.value() <= 0 or self.estimatedTriggerRate_spinbox.value() <= 0:
            self.estimatedTime_spinbox.setValue(0)
        else:
            self.estimatedTime_spinbox.setValue(self.numEvents_spinbox.value() / (self.estimatedTriggerRate_spinbox.value() * 1000) / 60.0)

