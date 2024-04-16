from PyQt5 import QtCore, QtGui, QtWidgets

class tab_digitizer_config(object):


    def __init__(self, MainWindow):
        self.common_config_dict = {
            "POST_TRIGGER": ("Post Trigger", 50, {"min": 0, "max": 100}),
            "PULSE_POLARITY": ("Pulse Polarity", 0, ["POSITIVE", "NEGATIVE"]),
            "EXTERNAL_TRIGGER": ("Ext. Trigger", 0, ["DISABLED", "ACQUISITION_ONLY", "ACQUISITION_AND_TRGOUT"]),
            "FAST_TRIGGER": ("Fast Trigger", 0, ["DISABLED", "ACQUISITION_ONLY"]),
            "ENABLED_FAST_TRIGGER_DIGITIZING": ("Digitize Trigger", 0, ["YES", "NO"]),
            "DRS4_FREQUENCY": ("Digitizer Frequency", 2, ["5 GHz", "2.5 GHz", "1 GHz", "750 MHz"]),
            "FPIO_LEVEL": ("Front Panel IO Level", 0, ["NIM", "TTL"]),
        }

        self.group_config_dict = {
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

        self.trigger_config_dict = {
            "DC_OFFSET": ("DC Offset", 0, {"min": 0, "max": 0xFFFF}),
            "THRESHOLD": ("Threshold", 0, {"min": 0, "max": 0xFFFF}),
            "TYPE": ("Type", 0, ["NIM", "Bipolar", "TTL", "Custom"]),
        }

        self.section_headers = [
            "[COMMON]",
            "[0]",
            "[1]",
            "[TR0]",
        ]

        self.config_list = [
            self.common_config_dict,
            self.group_config_dict,
            self.group_config_dict,
            self.trigger_config_dict
        ]

        self.device_input_list = {}


    def setupConfigureUI_section(self, device, i):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        input_list = self.device_input_list[device][self.section_headers[i]]

        pretty_headers = [
            "Common",
            "Group 0",
            "Group 1",
            "Trigger",
        ]

        layout.addRow(QtWidgets.QLabel(pretty_headers[i]))

        config = self.config_list[i]

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


    def setupConfigureUI(self, device):
        deviceConfigWidget = QtWidgets.QWidget()
        configLayout = QtWidgets.QHBoxLayout(deviceConfigWidget)

        self.device_input_list[device] = {}
        for i in range(4):
            self.device_input_list[device][self.section_headers[i]] = {}
            configLayout.addWidget(self.setupConfigureUI_section(device, i))
    
        self.device_input_list[device]['[TR0]']['TYPE'].currentTextChanged.connect(lambda text: self.trigger_type_changed(device, text))
        self.trigger_type_changed(device, self.device_input_list[device]['[TR0]']['TYPE'].currentText())

        return deviceConfigWidget

    def export_config(self, device):
        print(self.section_headers[0])
        for key in self.common_config_dict:
            widget = self.device_input_list[device][self.section_headers[0]][key]
            if type(widget) is QtWidgets.QComboBox:
                print('{} {}'.format(key, widget.currentText()))
            elif type(widget) is QtWidgets.QSpinBox:
                print('{} {}'.format(key, widget.value()))
        
        for g in range(2):
            header = self.section_headers[1+g]
            print(header)

            enable_input = 'ENABLE_INPUT'
            print('{} {}'.format(enable_input, self.device_input_list[device][header][enable_input].currentText()))

            grp_ch_offset = "GRP_CH_DC_OFFSET"
            for c in range(8):
                grp_ch_offset += " " + str(self.device_input_list[device][header]["CH{}_DC_OFFSET".format(c)].value())
            print(grp_ch_offset)

        print(self.section_headers[3])
        if self.device_input_list[device][self.section_headers[3]]["TYPE"].currentText() == "Custom":
            dc_offset = "DC_OFFSET"
            print('{} {}'.format(dc_offset, self.device_input_list[device][self.section_headers[3]][dc_offset].value()))

            threshold = "THRESHOLD"
            print('{} {}'.format(threshold, self.device_input_list[device][self.section_headers[3]][threshold].value()))
        else:
            ttype = "TYPE"
            print('{} {}'.format(ttype, self.device_input_list[device][self.section_headers[3]][ttype].currentText()))


    def trigger_type_changed(self, device, text):
        if text == 'Custom':
            self.device_input_list[device]['[TR0]']['DC_OFFSET'].setEnabled(True)
            self.device_input_list[device]['[TR0]']['THRESHOLD'].setEnabled(True)
        else:
            self.device_input_list[device]['[TR0]']['DC_OFFSET'].setEnabled(False)
            self.device_input_list[device]['[TR0]']['THRESHOLD'].setEnabled(False)
