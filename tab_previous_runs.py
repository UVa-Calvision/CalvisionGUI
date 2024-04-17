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

            for i, x in enumerate(run.to_dict().values()):
                item = QtWidgets.QTableWidgetItem()
                item.setText(x)
                self.config_table.setItem(row_index, i + 1, item)


    def config_exists(self, config_dict):
        for existing in self.existing_runs:
            d = existing.to_dict()
            matched = True
            for key in config_dict:
                if d[key] != config_dict[key]:
                    matched = False
                    break
            if matched:
                return True
        return False
