import os
import sys
import json

crystals = [
    "PbF2_6mm",
    "BGO_6mm",
    "PWO_6mm",
    "DSB-3",
    "ABSZL",
    "ABSC5",
    "BGO_18mm",
    "PWO_18mm",
    "SICBS01309",
]

sipm_types = [
    "Hamamatsu",
    "Broadband"
]

filter_types = [
    "None",
    "U330",
    "R64"
]

angles = [str(x) for x in [
    0,
    15,
    45,
    75,
    90,
    105,
    135,
    165,
    180,
]]

config_options = {
    'Crystal': crystals,
    'Front SiPM': sipm_types,
    'Front Filter': filter_types,
    'Back SiPM': sipm_types,
    'Back Filter': filter_types,
    'Angle': angles,
}

staging_area = '/home/uva/daq_staging'

class RunConfig:
    def __init__(self):
        self.run_number = 0
        self.crystal = None
        self.front_sipm_type = None
        self.front_filter_type = None
        self.back_sipm_type = None
        self.back_filter_type = None
        self.angle = None

    def new_config():
        run_numbers = [int(name[4:]) for name in os.listdir(staging_area) if name.startswith("run_")]
        for i in range(len(run_numbers)):
            if i not in run_numbers:
                config = RunConfig()
                config.run_number = i
                return config
        config = RunConfig()
        config.run_number = len(run_numbers)
        return config
            


    def to_dict(self):
        return {
            'Crystal': self.crystal,
            'Front SiPM': self.front_sipm_type,
            'Front Filter': self.front_filter_type,
            'Back SiPM': self.back_sipm_type,
            'Back Filter': self.back_filter_type,
            'Angle': self.angle,
        }

    def from_dict(self, d):
        self.crystal = d['Crystal']
        self.front_sipm_type = d['Front SiPM']
        self.front_filter_type = d['Front Filter']
        self.back_sipm_type = d['Back SiPM']
        self.back_filter_type = d['Back Filter']
        self.angle = d['Angle']

    def to_list(self):
        return list(self.to_dict().values())

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
        for i in run_numbers:
            c = RunConfig.open(i)
            if c != None:
                configs.append(c)
        return configs

    
    def get_path(self):
        return "/home/uva/daq_staging/run_{}/config.json".format(self.run_number)
