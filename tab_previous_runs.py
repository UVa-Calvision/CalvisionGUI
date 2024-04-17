from PyQt5 import QtWidgets, QtCore
from RunConfig import *
import itertools

class tab_previous_runs:
    
    def __init__(self, MainWindow):
        self.setup_UI(MainWindow)

    def setup_UI(self, MainWindow):
        sectionLayout = QtWidgets.QVBoxLayout(MainWindow)

        existingLabel = QtWidgets.QLabel()
        existingLabel.setText("Existing Runs")
        sectionLayout.addWidget(existingLabel)

        self.config_table = QtWidgets.QTableWidget()
        self.config_table.setColumnCount(7)
        self.config_table.setHorizontalHeaderLabels(["Run Number", "Crystal", "Front SiPM", "Front Filter", "Back SiPM", "Back Filter", "Angle"])
        sectionLayout.addWidget(self.config_table)

        # missingLabel = QtWidgets.QLabel()
        # missingLabel.setText("Missing Runs")
        # sectionLayout.addWidget(missingLabel)

        # self.missing_table = QtWidgets.QTableWidget()
        # self.missing_table.setColumnCount(6)
        # self.missing_table.setHorizontalHeaderLabels(["Crystal", "Front SiPM", "Front Filter", "Back SiPM", "Back Filter", "Angle"])
        # sectionLayout.addWidget(self.missing_table)

        self.update_run_table()


    def update_run_table(self):
        self.existing_runs = RunConfig.find_all()

        
        self.config_table.setRowCount(0)
        for run in self.existing_runs:
            row_index = self.config_table.rowCount()
            self.config_table.setRowCount(row_index + 1)
            
            item = QtWidgets.QTableWidgetItem()
            item.setText(str(run.run_number))
            self.config_table.setItem(row_index, 0, item)

            for i, x in enumerate(run.to_list()):
                item = QtWidgets.QTableWidgetItem()
                item.setText(x)
                self.config_table.setItem(row_index, i + 1, item)


        # options_lists = [config_options[key] for key in config_options]
        # missing_runs = [list(x) for x in itertools.product(*options_lists)]
        # self.missing_table.setRowCount(0)
        # for missing in missing_runs:
        #     if not self.config_exists(missing):
        #         self.add_row(self.missing_table, missing)
                


    def config_exists(self, config_list):
        for existing in self.existing_runs:
            if config_list == existing.to_list():
                return True
        return False
