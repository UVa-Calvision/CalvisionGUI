import os
import sys
import json

crystals = [
    "ABSC5",
    "ABSZL",
    "BGO_6cm",
    "BGO_18cm",
    "DSB-3",
    "PbF2_6cm",
    "PbF2_18cm",
    "PWO_6cm",
    "PWO_18cm",
    "SICBS01309",
    "LED_Calib",
    "Testing",
]

sipm_types = [
    "Broadcom",
    "Hamamatsu"
]

front_filter_types = [
    "None",
    "ND 1",
    "ND 1.3"
]

back_filter_types = [
    "None",
    "Everix 560",
    "Kodak 560",
    "Kodak 580",
    "O560",
    "600 2mm",
    "R640 1mm",
    "R640 2.5mm",
    "RG610",
    "U330",
]

angles = [str(x) for x in [
    -90,
    -45,
    -30,
    -15,
    0,
    15,
    30,
    45,
    90,
]]

config_options = {
    'Crystal': crystals,
    'Front SiPM': sipm_types,
    'Front Filter': front_filter_types,
    'Back SiPM': sipm_types,
    'Back Filter': back_filter_types,
    'Angle': angles,
}

staging_area = '/home/uva/daq_staging'

class RunConfig:
    def __init__(self):
        self.run_number = 0
        self.crystal = None
        self.front_sipm_type = None
        self.front_filter_type = None
        self.front_sipm_voltage = None
        self.back_sipm_type = None
        self.back_filter_type = None
        self.back_sipm_voltage = None
        self.angle = None

    # def new_config():
    #     run_numbers = [int(name[4:]) for name in os.listdir(staging_area) if name.startswith("run_")]
    #     for i in range(len(run_numbers)):
    #         if i not in run_numbers:
    #             config = RunConfig()
    #             config.run_number = i
    #             return config
    #     config = RunConfig()
    #     config.run_number = len(run_numbers)
    #     return config
 
    def make_next_run(self):
        run_numbers = [int(name[4:]) for name in os.listdir(staging_area) if name.startswith("run_")]
        self.run_number = max(run_numbers) + 1 if len(run_numbers) > 0 else 0
        self.save()


    def to_dict(self):
        return {
            'Crystal': self.crystal,
            'Front SiPM': self.front_sipm_type,
            'Front Filter': self.front_filter_type,
            'Front SiPM Voltage': self.front_sipm_voltage,
            'Back SiPM': self.back_sipm_type,
            'Back Filter': self.back_filter_type,
            'Back SiPM Voltage': self.back_sipm_voltage,
            'Angle': self.angle,
        }

    def from_dict(self, d):
        self.crystal = d['Crystal']
        self.front_sipm_type = d['Front SiPM']
        self.front_filter_type = d['Front Filter']
        self.back_sipm_type = d['Back SiPM']
        self.back_filter_type = d['Back Filter']
        self.angle = d['Angle']
        self.front_sipm_voltage = d['Front SiPM Voltage'] if 'Front SiPM Voltage' in d else None
        self.back_sipm_voltage = d['Back SiPM Voltage'] if 'Back SiPM Voltage' in d else None

    def open(run_number):
        config = RunConfig()
        config.run_number = run_number
        path = config.get_path()
        if not os.path.exists(path):
            return None

        with open(path, 'r') as infile:
            data = json.load(infile)
            config.from_dict(data)

        return config

    def save(self):
        path = self.get_path()
        run_dir = os.path.dirname(self.get_path())
        if not os.path.exists(run_dir):
            os.makedirs(run_dir, exist_ok = True)
        with open(path, 'w') as out:
            out.write(json.dumps(self.to_dict(), indent=4))

    def find_all():
        run_numbers = [int(name[4:]) for name in os.listdir(staging_area) if name.startswith("run_")]
        configs = []
        for i in sorted(run_numbers,reverse=True):
            c = RunConfig.open(i)
            if c != None:
                configs.append(c)
        return configs

    def run_name(self):
        return "run_{}".format(self.run_number)
    
    def get_path(self):
        return self.run_directory() + "/config.json"

    def run_directory(self):
        return staging_area + "/" + self.run_name()

    def hg_config_file(self):
        return self.run_directory() + "/hg_config.cfg"

    def lg_config_file(self):
        return self.run_directory() + "/lg_config.cfg"

    def hg_dump_file(self):
        return self.run_directory() + "/dump_HG"

    def lg_dump_file(self):
        return self.run_directory() + "/dump_LG"
