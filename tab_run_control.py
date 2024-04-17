from PyQt5 import QtWidgets, QtCore
from RunConfig import *


class tab_run_control(QtCore.QObject):
    
    request_check_repeat = QtCore.pyqtSignal()

    def __init__(self, MainWindow):
        super().__init__()
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)


        runWindow = QtWidgets.QWidget()
        runLayout = QtWidgets.QFormLayout(runWindow)
        sectionLayout.addWidget(runWindow)

        self.config_comboBoxes = {}
        for key in config_options:
            self.config_comboBoxes[key] = QtWidgets.QComboBox()
            self.config_comboBoxes[key].addItems(config_options[key])
            self.config_comboBoxes[key].setEditable(True)
            self.config_comboBoxes[key].currentTextChanged.connect(self.request_check_repeat)
            runLayout.addRow(key, self.config_comboBoxes[key])

        self.repeat_warning = QtWidgets.QLabel()
        runLayout.addRow(self.repeat_warning)

        makeRunButton = QtWidgets.QPushButton()
        makeRunButton.setText("Make Run")
        makeRunButton.clicked.connect(self.make_run)
        sectionLayout.addWidget(makeRunButton)

    def current_config_dict(self):
        config_values = {}
        for key in config_options:
            config_values[key] = self.config_comboBoxes[key].currentText()
        return config_values

    def make_run(self):
        config = RunConfig.new_config()
        config.from_dict(self.current_config_dict())
        config.save()
        self.request_check_repeat.emit()

    def update_repeat_warning(self, is_repeated):
        if is_repeated:
            self.repeat_warning.setText("WARNING: Run config already exists in staging area")
            self.repeat_warning.setStyleSheet("QLabel { color : red; }")
        else:
            self.repeat_warning.setText("Run config doesn't exist in staging area yet.")
            self.repeat_warning.setStyleSheet("QLabel { color : black; }")
