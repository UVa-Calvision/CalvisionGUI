import sys
sys.path.insert(0, '/home/uva/local_install/python/fygen')
import fygen


class TestHandle:
    def __init__(self):
        self.values = [{
                'enable': False,
                'volts': 0.0,
                'freq_hz': 0,
                'duty_cycle': 0.5,
                'offset_volts': 0,
                'wave': 'square',
        } for i in range(2)]

    def set(self, channel, wave = None, freq_hz = None, duty_cycle = None, volts = None, offset_volts = None, enable = None):
        v = self.values[channel]

        if wave != None:
            v['wave'] = wave

        if freq_hz != None:
            v['freq_hz'] = freq_hz

        if duty_cycle != None:
            v['duty_cycle'] = duty_cycle

        if volts != None:
            v['volts'] = volts

        if offset_volts != None:
            v['offset_volts'] = offset_volts

        if enable != None:
            v['enable'] = enable

    def get(self, channel, params):
        return self.values[channel][params]


def find_ttyUSB(device):
    '''Return ttyUSB# for device
    Example Calvision search strings:
      find_ttyUSB(Adafruit_Metro)
      find_ttyUSB(QinHeng)  # for pulser
    '''
    for ttyUSB in glob.glob('/dev/ttyUSB*'):
        command = f'udevadm info --name={ttyUSB} | grep {device} > /dev/null'
        status = subprocess.run(command, shell = True)
        if status.returncode == 0:
            return ttyUSB
    return None


class Pulser:

    led_channel = fygen.CH1
    holdoff_channel = fygen.CH2


    def __init__(self):
        self.handle = None

    def open(self):
        # self.handle = TestHandle()
        dev = find_ttyUSB('QinHeng')
        if dev == None:
            print('*** Error: FeelTech pulser not found ***')
        else:
            self.handle = fygen.FYGen(dev, device_name = 'fy2300h')
            print(f'--- FeelTech pulser found at {dev} ---')


    def close(self):
        self.handle = None

    def is_open(self):
        return self.handle != None

    def set_enabled(self, channel, enable):
        self.handle.set(channel = channel, enable = enable)

    def is_enabled(self, channel):
        return self.handle.get(channel = channel, params = 'enable')

    def get_voltage(self, channel):
        return self.handle.get(channel = channel, params = 'volts')

    def get_frequency(self, channel):
        return self.handle.get(channel = channel, params = 'freq_hz')

    def get_duty(self, channel):
        return self.handle.get(channel = channel, params = 'duty_cycle')

    def get_offset_voltage(self, channel):
        return self.handle.get(channel = channel, params = 'offset_volts')

    def get_all(self, channel):
        results = {}
        for c in ['enable', 'volts', 'freq_hz', 'duty_cycle', 'offset_volts']:
            results[c] = self.handle.get(channel = channel, params = c)
        return results


    def set_square(self, channel, frequency, duty, voltage, offset):
        self.handle.set(
                channel = channel,
                wave = 'square',
                freq_hz = frequency,
                duty_cycle = duty,
                volts = voltage,
                offset_volts = offset)


    def set_default_led(self):
        self.set_square(channel = Pulser.led_channel,
                        frequency = 500, 
                        duty = 1e-3,
                        voltage = 5.0,
                        offset = 5.0 / 2.0)

    def set_default_holdoff(self):
        self.set_square(channel = Pulser.holdoff_channel,
                        frequency = 1,
                        duty = 0.99,
                        voltage = 0.5,
                        offset = 4.5)

    def set_default(self, channel):
        if channel == Pulser.led_channel:
            self.set_default_led()
        elif channel == Pulser.holdoff_channel:
            self.set_default_holdoff()

    def all_off(self):
        self.set_enabled(Pulser.led_channel, False)
        self.set_enabled(Pulser.holdoff_channel, False)
