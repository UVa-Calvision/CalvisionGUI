from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Pulser import *
import pyqtgraph as pg


class PulserWidget(QWidget):

    control_change = pyqtSignal(bool, bool)

    def __init__(self, pulser, channel, name):
        super().__init__()
        self.pulser = pulser
        self.channel = channel
        self.name = name

        sectionLayout = QVBoxLayout(self)
        
        controlWindow = QWidget()
        controlLayout = QFormLayout(controlWindow)
        controlLayout.setHorizontalSpacing(20)
        sectionLayout.addWidget(controlWindow)

        label = QLabel()
        label.setText(name)
        controlLayout.addRow(label)
        controlLayout.setAlignment(label, Qt.AlignHCenter)

        # Status

        label = QLabel()
        label.setText("Status")
        controlLayout.addRow(label)
        controlLayout.setAlignment(label, Qt.AlignLeft)

        self.status_enabled = QLabel()
        controlLayout.addRow("Enabled", self.status_enabled)

        self.status_frequency = QLabel()
        controlLayout.addRow("Frequency", self.status_frequency)

        self.status_duty = QLabel()
        controlLayout.addRow("Duty Cycle", self.status_duty)

        self.status_voltage = QLabel()
        controlLayout.addRow("Voltage", self.status_voltage)

        self.status_offset = QLabel()
        controlLayout.addRow("Offset", self.status_offset)

        self.default_setup_button = QPushButton()
        self.default_setup_button.setText("Default Setup")
        self.default_setup_button.clicked.connect(lambda: self.set_default)
        controlLayout.addRow(self.default_setup_button)

        spacer = QSpacerItem(0, 50)
        controlLayout.addItem(spacer)

        # Controls

        label = QLabel()
        label.setText("Controls")
        controlLayout.addRow(label)
        controlLayout.setAlignment(label, Qt.AlignLeft)

        self.enabled_checkbox = QCheckBox()
        controlLayout.addRow("Enable", self.enabled_checkbox)
        
        self.frequency_spinbox = QSpinBox()
        self.frequency_spinbox.setRange(0, 10000)
        self.frequency_spinbox.setSuffix(" Hz")
        controlLayout.addRow("Frequency", self.frequency_spinbox)

        self.duty_spinbox = QDoubleSpinBox()
        self.duty_spinbox.setRange(0, 100)
        self.duty_spinbox.setSuffix(" %")
        controlLayout.addRow("Duty Cycle", self.duty_spinbox)

        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(0, 10)
        self.voltage_spinbox.setSuffix(" V")
        controlLayout.addRow("Voltage", self.voltage_spinbox)

        self.offset_spinbox = QDoubleSpinBox()
        self.offset_spinbox.setRange(-10, 10)
        self.offset_spinbox.setSuffix(" V")
        controlLayout.addRow("Offset", self.offset_spinbox)

        self.apply_button = QPushButton()
        self.apply_button.setText("Apply")
        self.apply_button.clicked.connect(self.apply)
        controlLayout.addRow(self.apply_button)

        # Sample waveform plot

        layoutWidget = pg.GraphicsLayoutWidget()
        layoutWidget.setBackground('w')
        
        pen = pg.mkPen(color = 'b', width = 3)
        styles = {"color": "red", "font-size": "12px"}

        self.plot = layoutWidget.addPlot()
        self.plot.setTitle("Sample Waveform", color = 'b', size = '10pt')
        self.plot.setLabel("left", "Waveform (V)", **styles)
        self.plot.setLabel("bottom", "Time (s)", **styles)
        self.plot.addLegend()
        self.plot.showGrid(x = True, y = True)

        self.waveform_line = self.plot.plot([0], [0], pen = pen)

        sectionLayout.addWidget(layoutWidget)

        # Update state

        self.sync_with_pulser()


    def set_default(self, enabled = False):
        print("Applying pulser default settings, may take a long time...")
        self.pulser.set_default(self.channel)
        self.pulser.set_enabled(self.channel, enabled)
        self.sync_with_pulser(True)

    def apply(self):
        print("Applying pulser settings, may take a long time...")
        self.pulser.set_square(
                channel = self.channel,
                frequency = self.frequency_spinbox.value(),
                duty = self.duty_spinbox.value() / 100.0,
                voltage = self.voltage_spinbox.value(),
                offset = self.offset_spinbox.value())
        self.pulser.set_enabled(self.channel, self.enabled_checkbox.isChecked())
        self.sync_with_pulser()

    def plot_sample_waveform(self, values):
        self.plot.autoRange()
        if values['freq_hz'] <= 0:
            self.waveform_line.setVisible(False)
        else:
            period = 1.0 / values['freq_hz']
            delay = 0
            times = [0,
                     delay,
                     delay,
                     delay + values['duty_cycle'] * period,
                     delay + values['duty_cycle'] * period,
                     period]
            volts = [-values['offset_volts'],
                     -values['offset_volts'],
                     -values['offset_volts'] + values['volts'],
                     -values['offset_volts'] + values['volts'],
                     -values['offset_volts'],
                     -values['offset_volts']]
            self.waveform_line.setData(times, volts)
            self.waveform_line.setVisible(True)
            
            padding_ratio = 0.01
            x_padding = padding_ratio * period
            y_padding = padding_ratio * values['volts']
            self.plot.setLimits(
                    xMin = -x_padding,
                    xMax = period + x_padding,
                    yMin = -values['offset_volts'] - y_padding,
                    yMax = -values['offset_volts'] + values['volts'] + y_padding,
                    minXRange = padding_ratio * values['duty_cycle'] * period,
                    maxXRange = (1 + padding_ratio) * period,
                    minYRange = (1 + 2 * padding_ratio) * values['volts'],
                    maxYRange = (1 + 2 * padding_ratio) * values['volts']
            )

    def sync_with_pulser(self, force_controls = False):
        if self.pulser.is_open():
            values = self.pulser.get_all(self.channel)

            self.status_enabled.setText("On" if values['enable'] else "Off")
            self.status_frequency.setText("{} Hz".format(values['freq_hz']))
            self.status_duty.setText("{} %".format(values['duty_cycle'] * 100.0))
            self.status_voltage.setText("{} V".format(values['volts']))
            self.status_offset.setText("{} V".format(values['offset_volts']))

            if force_controls:
                self.enabled_checkbox.setChecked(values['enable'])
                self.frequency_spinbox.setValue(values['freq_hz'])
                self.duty_spinbox.setValue(values['duty_cycle'] * 100.0)
                self.voltage_spinbox.setValue(values['volts'])
                self.offset_spinbox.setValue(values['offset_volts'])

            self.plot_sample_waveform(values)
            self.control_change.emit(True, values['enable'])

        else:
            self.status_enabled.setText('-')
            self.status_frequency.setText('- Hz')
            self.status_duty.setText('- %')
            self.status_voltage.setText('- V')
            self.status_offset.setText('- V')
            self.waveform_line.setVisible(False)
            self.control_change.emit(False, False)

        self.enabled_checkbox.setEnabled(self.pulser.is_open())
        self.frequency_spinbox.setEnabled(self.pulser.is_open())
        self.duty_spinbox.setEnabled(self.pulser.is_open())
        self.voltage_spinbox.setEnabled(self.pulser.is_open())
        self.offset_spinbox.setEnabled(self.pulser.is_open())
        self.apply_button.setEnabled(self.pulser.is_open())
        self.default_setup_button.setEnabled(self.pulser.is_open())

    def enable_controls(self, enable):
        self.enabled_checkbox.setChecked(enable)
        self.apply()



class tab_pulser(QObject):

    def __init__(self, run_config, run_status, MainWindow):
        super().__init__()
        self.config = run_config
        self.status = run_status
        self.pulser = Pulser()
        self.setup_UI(MainWindow)


    def setup_UI(self, MainWindow):
        sectionLayout = QVBoxLayout(MainWindow)

        deviceWindow = QWidget()
        deviceLayout = QGridLayout(deviceWindow)
        sectionLayout.addWidget(deviceWindow)

        row = 0
        column = 0
        label = QLabel()
        label.setText("Pulser Device")
        deviceLayout.addWidget(label, row, column)

        column += 1
        self.open_checkbox = QCheckBox()
        self.open_checkbox.setText("Open")
        self.open_checkbox.clicked.connect(self.open_pulser)
        deviceLayout.addWidget(self.open_checkbox, row, column)

        pulserWindow = QWidget()
        pulserLayout = QHBoxLayout(pulserWindow)
        sectionLayout.addWidget(pulserWindow)

        self.led_pulser = PulserWidget(self.pulser, Pulser.led_channel, "LED")
        pulserLayout.addWidget(self.led_pulser)

        self.holdoff_pulser = PulserWidget(self.pulser, Pulser.holdoff_channel, "Hold Off")
        pulserLayout.addWidget(self.holdoff_pulser)

    def open_pulser(self):
        if self.open_checkbox.isChecked():
            print("Attempting to open pulser")
            self.pulser.open()
        else:
            print("Attempting to close pulser")
            self.pulser.close()
        self.open_checkbox.setChecked(self.pulser.is_open())
        self.led_pulser.sync_with_pulser()
        self.holdoff_pulser.sync_with_pulser()

    def power_off(self):
        self.pulser.all_off()
        self.pulser.close()

    def setup(self):
        self.open_checkbox.click()
        if self.pulser.is_open():
            self.led_pulser.set_default(enabled = False)
            self.holdoff_pulser.set_default(enabled = True)
