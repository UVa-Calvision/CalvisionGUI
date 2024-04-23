from PyQt5 import QtCore, QtGui, QtWidgets

common_config_dict = {
    "POST_TRIGGER": ("Post Trigger", 50, {"min": 0, "max": 100}),
    "PULSE_POLARITY": ("Pulse Polarity", 0, ["POSITIVE", "NEGATIVE"]),
    "EXTERNAL_TRIGGER": ("Ext. Trigger", 0, ["DISABLED", "ACQUISITION_ONLY", "ACQUISITION_AND_TRGOUT"]),
    "FAST_TRIGGER": ("Fast Trigger", 1, ["DISABLED", "ACQUISITION_ONLY"]),
    "ENABLED_FAST_TRIGGER_DIGITIZING": ("Digitize Trigger", 0, ["YES", "NO"]),
    "DRS4_FREQUENCY": ("Digitizer Frequency", 2, ["5 GHz", "2.5 GHz", "1 GHz", "750 MHz"]),
    "FPIO_LEVEL": ("Front Panel IO Level", 0, ["NIM", "TTL"]),
    "MAX_NUM_EVENTS_BLT": ("Max Number of Events Per Readout", 1000, {"min": 0, "max": 1023}),
    "MAX_READOUT_COUNT": ("Max Event Readout Count (0 = no max)", 50000, {"min": 0, "max": 60 * 60 * 5000}),
}

group_config_dict = {
    "ENABLE_INPUT": ("Enable", 0, ["YES", "NO"]),
    "CH0_DC_OFFSET": ("Ch0 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH1_DC_OFFSET": ("Ch1 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH2_DC_OFFSET": ("Ch2 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH3_DC_OFFSET": ("Ch3 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH4_DC_OFFSET": ("Ch4 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH5_DC_OFFSET": ("Ch5 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH6_DC_OFFSET": ("Ch6 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
    "CH7_DC_OFFSET": ("Ch7 DC Offset", 0x7FFF, {"min": 0, "max": 0xFFFF}),
}

trigger_config_dict = {
    "DC_OFFSET": ("DC Offset", 0, {"min": 0, "max": 0xFFFF}),
    "THRESHOLD": ("Threshold", 0, {"min": 0, "max": 0xFFFF}),
    "TYPE": ("Type", 0, ["NIM", "Bipolar", "TTL", "Custom"]),
}

common_section  = 0
group_0_section = 1
group_1_section = 2
trigger_section = 3

section_headers = [
    "[COMMON]",
    "[0]",
    "[1]",
    "[TR0]",
]

config_list = [
    common_config_dict,
    group_config_dict,
    group_config_dict,
    trigger_config_dict
]



class tab_digitizer_config(object):
    def __init__(self, run_config, MainWindow):
        self.run_config = run_config
        self.device_input_list = [{} for x in section_headers]
        self.setupUi(MainWindow)


    def setupConfigureUI_section(self, i):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        input_list = self.device_input_list[i]

        pretty_headers = [
            "Common",
            "Group 0",
            "Group 1",
            "Trigger",
        ]

        layout.addRow(QtWidgets.QLabel(pretty_headers[i]))

        config = config_list[i]

        for key in config:
            label_text = config[key][0]
            default_value = config[key][1]
            bounds = config[key][2]

            input_widget = None
            if type(bounds) is dict:
                input_widget = QtWidgets.QSpinBox(widget)
                input_widget.setRange(bounds["min"], bounds["max"])
                input_widget.setValue(default_value)
            elif type(bounds) is list:
                input_widget = QtWidgets.QComboBox(widget)
                input_widget.addItems(bounds)
                input_widget.setCurrentIndex(default_value)
            else:
                print("something's wrong...")
                input_widget = QtWidgets.QLabel("No specified bounds?")

            layout.addRow(label_text, input_widget)
            input_list[key] = input_widget

        return widget


    def setupUi(self, MainWindow):
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)

        configWindow = QtWidgets.QWidget()
        configLayout = QtWidgets.QHBoxLayout(configWindow)
        sectionLayout.addWidget(configWindow)

        for i in range(len(section_headers)):
            configLayout.addWidget(self.setupConfigureUI_section(i))
    
        self.device_input_list[trigger_section]['TYPE'].currentTextChanged.connect(self.trigger_type_changed)
        self.trigger_type_changed(self.device_input_list[trigger_section]['TYPE'].currentText())

        exportWindow = QtWidgets.QWidget()
        exportLayout = QtWidgets.QGridLayout(exportWindow)
        sectionLayout.addWidget(exportWindow)

        row = 0
        column = 0
        exportLabel = QtWidgets.QLabel()
        exportLabel.setText("Export Configuration")
        exportLayout.addWidget(exportLabel, row, column)

        column += 1
        self.exportPath_textbox = QtWidgets.QLineEdit()
        self.exportPath_textbox.setText("/home/uva/daq_staging/defaults/")
        exportLayout.addWidget(self.exportPath_textbox, row, column)

        column += 1
        exportBrowse_button = QtWidgets.QPushButton()
        exportBrowse_button.setText("Browse")
        exportBrowse_button.clicked.connect(lambda: self.open_file(self.exportPath_textbox, mode = QtWidgets.QFileDialog.AcceptSave))
        exportLayout.addWidget(exportBrowse_button, row, column)

        column += 1
        exportButton = QtWidgets.QPushButton()
        exportButton.setText("Export")
        exportButton.clicked.connect(self.export_config)
        exportLayout.addWidget(exportButton, row, column)

        row += 1
        column = 0
        importLabel = QtWidgets.QLabel()
        importLabel.setText("Import Configuration")
        exportLayout.addWidget(importLabel, row, column)

        column += 1
        self.importPath_textbox = QtWidgets.QLineEdit()
        self.importPath_textbox.setText("/home/uva/daq_staging/defaults/")
        exportLayout.addWidget(self.importPath_textbox, row, column)

        column += 1
        importBrowse_button = QtWidgets.QPushButton()
        importBrowse_button.setText("Browse")
        importBrowse_button.clicked.connect(lambda: self.open_file(self.importPath_textbox, mode = QtWidgets.QFileDialog.AcceptOpen))
        exportLayout.addWidget(importBrowse_button, row, column)

        column += 1
        importButton = QtWidgets.QPushButton()
        importButton.setText("Import")
        importButton.clicked.connect(self.import_config)
        exportLayout.addWidget(importButton, row, column)


    def open_file(self, path_textbox, mode):
        dialog = QtWidgets.QFileDialog(path_textbox)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilter("Digitzer Config (*.cfg)")
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        dialog.setAcceptMode(mode)
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            if len(fileNames) > 0:
                path_textbox.setText(fileNames[0])

    def import_config(self):
        self.load_config(self.importPath_textbox.displayText())

    def load_config(self, path):
        with open(path, 'r') as infile:
            section = 0
            for line in infile:
                line = line.strip()
                if line == section_headers[common_section]:
                    section = common_section
                elif line == section_headers[group_0_section]:
                    section = group_0_section
                elif line == section_headers[group_1_section]:
                    section = group_1_section
                elif line == section_headers[trigger_section]:
                    section = trigger_section
                else:
                    items = line.split()
                    if len(items) < 2:
                        continue
                    
                    key = items[0]
                    if key in config_list[section]:
                        value = items[1]
                        bounds = config_list[section][key][2]
                        if type(bounds) is dict:
                            value = int(value)
                            if section == trigger_section and (key == 'DC_OFFSET' or key == 'THRESHOLD'):
                                self.device_input_list[trigger_section]['TYPE'].setCurrentText('Custom')
                                self.trigger_type_changed('Custom')
                            if (value <= bounds['max']) and (value >= bounds['min']):
                                self.device_input_list[section][key].setValue(value)
                        elif type(bounds) is list:
                            for i in range(len(bounds)):
                                if bounds[i] == value:
                                    self.device_input_list[section][key].setCurrentIndex(i)
                                    if section == trigger_section and key == 'TYPE':
                                        self.trigger_type_changed(value)
                                    break
                    elif key == "GRP_CH_DC_OFFSET" and len(items) == 9:
                        for c in range(8):
                            self.device_input_list[section]["CH{}_DC_OFFSET".format(c)].setValue(int(items[1+c]))



    def export_config(self):
        self.write_config(self.exportPath_textbox.displayText())

    def write_config(self, path):
        with open(path, 'w') as out:
            out.write(section_headers[common_section] + "\n")
            for key in common_config_dict:
                widget = self.device_input_list[0][key]
                if key == 'DRS4_FREQUENCY':
                    out.write('{} {}\n'.format(key, widget.currentIndex()))
                elif type(widget) is QtWidgets.QComboBox:
                    out.write('{} {}\n'.format(key, widget.currentText()))
                elif type(widget) is QtWidgets.QSpinBox:
                    out.write('{} {}\n'.format(key, widget.value()))
            
            for g in range(2):
                header = section_headers[1+g]
                out.write(header + "\n")

                for key in group_config_dict:
                    widget = self.device_input_list[1+g][key]
                    if type(widget) is QtWidgets.QComboBox:
                        out.write('{} {}\n'.format(key, widget.currentText()))
                    elif type(widget) is QtWidgets.QSpinBox:
                        out.write('{} {}\n'.format(key, widget.value()))
                       
            out.write(section_headers[trigger_section] + "\n")
            if self.device_input_list[trigger_section]["TYPE"].currentText() == "Custom":
                dc_offset = "DC_OFFSET"
                out.write('{} {}\n'.format(dc_offset, self.device_input_list[trigger_section][dc_offset].value()))

                threshold = "THRESHOLD"
                out.write('{} {}\n'.format(threshold, self.device_input_list[trigger_section][threshold].value()))
            else:
                ttype = "TYPE"
                out.write('{} {}\n'.format(ttype, self.device_input_list[trigger_section][ttype].currentText()))


    def trigger_type_changed(self, text):
        if text == 'Custom':
            self.device_input_list[trigger_section]['DC_OFFSET'].setEnabled(True)
            self.device_input_list[trigger_section]['THRESHOLD'].setEnabled(True)
        else:
            self.device_input_list[trigger_section]['DC_OFFSET'].setEnabled(False)
            self.device_input_list[trigger_section]['THRESHOLD'].setEnabled(False)
