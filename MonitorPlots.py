from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg


class MonitorPlots(QtCore.QObject):
    
    request_monitor_data = QtCore.pyqtSignal()

    def __init__(self, status):
        super().__init__()
        pg.setConfigOptions(antialias=True)        

        self.layoutWidget = pg.GraphicsLayoutWidget()
        self.layoutWidget.setBackground('w')

        self.pen = pg.mkPen(color='b', width=3)
        self.styles = {"color": "red", "font-size": "12px"}

        self.times = []
        self.y_values = []
        self.lines = []
        self.run_status = status
        self.is_monitoring = False
        self.run_status.update_timer.timeout.connect(self.monitor_callback)

        self.start_button = QtWidgets.QPushButton()
        self.start_button.setEnabled(True)
        self.start_button.setText("Monitor Start")
        self.start_button.clicked.connect(self.start_monitor)

        self.stop_button = QtWidgets.QPushButton()
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Monitor Stop")
        self.stop_button.clicked.connect(self.stop_monitor)

    def make_plot(self, title, ylabel, use_log = False):
        plot = self.layoutWidget.addPlot()
        plot.setTitle(title, color = 'b', size = '10pt')
        plot.setLabel("left", ylabel, **self.styles)
        plot.setLabel("bottom", "Time (sec)", **self.styles)
        plot.addLegend()
        plot.showGrid(x = True, y = True)
        if use_log:
            plot.setLogMode(y = True)

        self.times.append([])
        self.y_values.append([])
        self.lines.append(plot.plot([0], [0], pen = self.pen))

    def make_waveform_plot(self, title, legend_fmt, n):
        plot = self.layoutWidget.addPlot()
        plot.setTitle(title, color = 'b', size = '10pt')
        plot.setLabel("left", "Channel (mV)", **self.styles)
        plot.setLabel("bottom", "Time (ns)", **self.styles)

        legend = pg.LegendItem(horSpacing = 0, frame = False, colCount = 1)
        self.layoutWidget.addItem(legend)

        for i in range(n):
            self.times.append([])
            self.y_values.append([])
            self.lines.append(plot.plot([0], [0], pen = pg.intColor(i), name = legend_fmt.format(i)))
            legend.addItem(self.lines[-1], legend_fmt.format(i))
      

    def add_point(self, i, y):
        self.times[i].append(self.run_status.monitor_time)
        self.y_values[i].append(y)
        self.lines[i].setData(self.times[i], self.y_values[i])

    def set_data(self, i, ts, ys):
        self.times[i] = ts
        self.y_values[i] = ys
        self.lines[i].setData(self.times[i], self.y_values[i])

    def get_layout_widget(self):
        return self.layoutWidget
        

    def reset(self):
        for i in range(len(self.lines)):
            self.times[i] = []
            self.y_values[i] = []
            self.lines[i].setData([0], [0])

    def start_monitor(self):
        self.is_monitoring = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_monitor(self):
        self.is_monitoring = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def run_start(self):
        self.reset()
        self.is_monitoring = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def run_stop(self):
        self.is_monitoring = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def monitor_callback(self):
        if self.is_monitoring:
            self.request_monitor_data.emit()
