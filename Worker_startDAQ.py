from PyQt5.QtCore import *
import time
from CallProcess import *
import struct

class Worker_startDAQ(QObject,CallProcess):
    finished = pyqtSignal()

    def __init__(self, run_config):
        super(Worker_startDAQ, self).__init__()
        self.run_config = run_config

    def run(self):
        run_name = self.run_config.run_name()
        hg_config = self.run_config.hg_config_file()
        lg_config = self.run_config.lg_config_file()
        source_conda = "source /home/uva/miniforge3/etc/profile.d/conda.sh; conda activate calvision;"
        CallProcess.run(self, source_conda + "/home/uva/local_install/bin/dual_readout {} {} {}".format(run_name, hg_config, lg_config))

        self.finished.emit()

    def handle_output(self, line):
        print(line)

    def stop(self):
        self.message("stop\n")

    def single_plot(self):
        self.message("sample plot\n")

        # Briefly wait for the files to be created and filled (sleep ~100ms)
        QThread.currentThread().msleep(100)

        hg_times, hg_channels = self.read_dump_file(self.run_config.hg_dump_file())
        lg_times, lg_channels = self.read_dump_file(self.run_config.lg_dump_file())

        return (hg_times, hg_channels, lg_times, lg_channels)

    def read_dump_file(self, path):
        try:
            fd = os.open(path, os.O_RDONLY)
            raw_times = os.read(fd, 8 * 1024)
            times = []
            for t in struct.iter_unpack('@d', raw_times):
                times.append(t[0])

            channels = []
            for c in range(8):
                channels.append([])
                raw_channel = os.read(fd, 4 * 1024)
                for t in struct.iter_unpack('@f', raw_channel):
                    channels[c].append(t[0])

            os.close(fd)

            return (times, channels)
        except Exception as e:
            return (None, None)

class Reset_DAQ(CallProcess):
    def run(self):
        source_conda = "source /home/uva/miniforge3/etc/profile.d/conda.sh; conda activate calvision;"
        CallProcess.run(self, source_conda + "/home/uva/local_install/bin/reset_digitizer")

    def handle_output(self, line):
        print(line)

    def execute():
        Reset_DAQ().run()

