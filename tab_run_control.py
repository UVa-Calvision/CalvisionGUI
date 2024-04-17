from PyQt5 import QtWidgets, QtCore
from RunConfig import *


class tab_run_control(QtCore.QObject):
    
    run_config_changed = QtCore.pyqtSignal()
    begin_run = QtCore.pyqtSignal()
    end_run = QtCore.pyqtSignal()

    def __init__(self, run_config, MainWindow):
        super().__init__()
        self.run_config = run_config
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
            self.config_comboBoxes[key].currentTextChanged.connect(self.run_config_changed)
            runLayout.addRow(key, self.config_comboBoxes[key])

        self.repeat_warning = QtWidgets.QLabel()
        runLayout.addRow(self.repeat_warning)

        # statusWindow = QtWidgets.QWidget()
        # statusWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        # statusLayout = QtWidgets.QFormlayout(statusWindow)
        # sectionLayout.addWidget(statusWindow)
        # 

        # self.statusLabel_local_time = QLabel()
        # statusLayout.addRow("Local Time: ", self.statusLabel_local_time)

        # self.statusLabel_run_time = QLabel()
        # statusLayout.addRow("Run Time: ", self.statusLabel_run_time)


        runButtonWindow = QtWidgets.QWidget()
        runButtonWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        runButtonLayout = QtWidgets.QHBoxLayout(runButtonWindow)
        sectionLayout.addWidget(runButtonWindow)

        self.beginRunButton = QtWidgets.QPushButton()
        self.beginRunButton.setText("Begin Run")
        self.beginRunButton.clicked.connect(self.begin_run)
        self.beginRunButton.setEnabled(True)
        runButtonLayout.addWidget(self.beginRunButton)

        self.endRunButton = QtWidgets.QPushButton()
        self.endRunButton.setText("End Run")
        self.endRunButton.clicked.connect(self.end_run)
        self.endRunButton.setEnabled(False)
        runButtonLayout.addWidget(self.endRunButton)

        # Connect signals and slots

        self.run_config_changed.connect(self.update_config)
        self.begin_run.connect(self.begin_run_button)
        self.end_run.connect(self.end_run_button)

        # Update state

        self.update_config()


    def begin_run_button(self):
        self.beginRunButton.setEnabled(False)
        self.endRunButton.setEnabled(True)
        for box in self.config_comboBoxes:
            self.config_comboBoxes[box].setEnabled(False)

    def end_run_button(self):
        self.beginRunButton.setEnabled(True)
        self.endRunButton.setEnabled(False)
        for box in self.config_comboBoxes:
            self.config_comboBoxes[box].setEnabled(True)

    def update_config(self):
        config_values = {}
        for key in config_options:
            config_values[key] = self.config_comboBoxes[key].currentText()
        self.run_config.from_dict(config_values)

    def update_repeat_warning(self, is_repeated):
        if is_repeated:
            self.repeat_warning.setText("WARNING: Run config already exists in staging area")
            self.repeat_warning.setStyleSheet("QLabel { color : red; }")
        else:
            self.repeat_warning.setText("Run config doesn't exist in staging area yet.")
            self.repeat_warning.setStyleSheet("QLabel { color : black; }")
