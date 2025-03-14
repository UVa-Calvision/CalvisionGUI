from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from functools import partial

def create_checkbox(label, row, column, width, slot_function, setchecked=False, layout=None):
    if layout is None:
        raise ValueError("Layout must be provided for checkbox placement.")
    checkbox = QtWidgets.QCheckBox()
    checkbox.setText(label)
    checkbox.setChecked(setchecked)
    layout.addWidget(checkbox, row, column, 1, width)
    checkbox.stateChanged.connect(slot_function)
    return checkbox

def create_button(label, row, column, width, slot_function, layout=None):
    if layout is None:
        raise ValueError("Layout must be provided for button placement.")
    button = QtWidgets.QPushButton()
    button.setText(label)
    layout.addWidget(button, row, column, 1, width)
    button.clicked.connect(slot_function)
    return button

def create_spinbox(label, row, column, width, slot_function=0, initvalue=0, layout=None):
    qlabel = QtWidgets.QLabel(label)
    layout.addWidget(qlabel, row, column, 1, width)

    if layout is None:
        raise ValueError("Layout must be provided for spinbox placement.")
    spinbox = QtWidgets.QSpinBox()
    spinbox.setMaximum(2**24-1)
    spinbox.setValue(initvalue)

    layout.addWidget(spinbox, row, column+1, 1, width)
    if slot_function:
        spinbox.valueChanged.connect(slot_function)
    return spinbox

def create_double_spinbox(label, row, column, width, slot_function=0, initvalue=0, layout=None):
    qlabel = QtWidgets.QLabel(label)
    layout.addWidget(qlabel, row, column, 1, width)

    if layout is None:
        raise ValueError("Layout must be provided for spinbox placement.")
    spinbox = QtWidgets.QDoubleSpinBox()
    spinbox.setDecimals(3)  # Set precision (3 decimal places)
    spinbox.setMinimum(-5.0)  # Min value
    spinbox.setMaximum(5.0)  # Max value
    spinbox.setSingleStep(0.1)  # Step size
    spinbox.setValue(initvalue)

    layout.addWidget(spinbox, row, column+1, 1, width)
    if slot_function:
        spinbox.valueChanged.connect(slot_function)
    return spinbox

def create_lineedit(label, row, column, width, initvalue='', layout=None):
    qlabel = QtWidgets.QLabel(label)
    layout.addWidget(qlabel, row, column, 1, width)

    if layout is None:
        raise ValueError("Layout must be provided for spinbox placement.")
    lineedit = QtWidgets.QLineEdit()
    lineedit.setText(initvalue)
    layout.addWidget(lineedit, row, column+1, 1, width)
    return lineedit


