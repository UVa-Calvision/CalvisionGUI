from PyQt5.QtCore import *
import time
from CallProcess import *
import struct




class Worker_startDAQ(QObject,CallProcess):
    finished = pyqtSignal()
    # update_log_file_name = pyqtSignal(str)

    def __init__(self):
        super(Worker_startDAQ, self).__init__()

    def run(self):
        run_name = "test"
        hg_config = "/home/uva/calvision/CalvisionDaq/data/config_file_1.txt"
        lg_config = "/home/uva/calvision/CalvisionDaq/data/config_file_2.txt"
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

        run_name = "test"

        hg_times, hg_channels = self.read_dump_file('/home/uva/daq_staging/{}/dump_HG'.format(run_name))
        lg_times, lg_channels = self.read_dump_file('/home/uva/daq_staging/{}/dump_LG'.format(run_name))

        return (hg_times, hg_channels, lg_times, lg_channels)

    def read_dump_file(self, path):
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


class Reset_DAQ(CallProcess):
    def run(self):
        source_conda = "source /home/uva/miniforge3/etc/profile.d/conda.sh; conda activate calvision;"
        CallProcess.run(self, source_conda + "/home/uva/local_install/bin/reset_digitizer")

    def handle_output(self, line):
        print(line)

    def execute():
        Reset_DAQ().run()

