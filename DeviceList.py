from pathlib import Path


class DeviceList:
    def __init__(self):
        self.caen_hv_devices = []
        self.caen_digi_devices = []
        self.rotor_device = None

        self.find_devices()

    def find_devices(self):
        dev_path = Path('/dev')
        self.caen_hv_devices = [str(x) for x in dev_path.glob('CAEN*')]
        self.caen_digi_devices = [str(x) for x in dev_path.glob('v1718_*')]
        self.rotor_device = str(dev_path / 'ROTOR')
