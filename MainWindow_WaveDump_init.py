from MainWindow_WaveDump import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import datetime
import sys, os, getopt
import logging
from PyQt5.QtCore import *



class StartQT5(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        current_dir = os.getcwd()
        self.logfilename = os.path.normpath(current_dir+'/log.txt')
        
        # if os.system("g++ WaveDump.c") == 0:
        #     print("Worked")
        # else:
        #     print("Failed")

    def normalOutputWritten(self,text): # this is the slot of the signal textWritten in EmittingStream
        self.ui.textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.ui.textBrowser.insertPlainText(text)
        self.logfile = open(self.logfilename,'a')
        self.logfile.write(text)

        # self.logfile = close()
#
class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        if text == '\n':
            text = text
        else:
            text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ">>" + text
        self.textWritten.emit(str(text)) # this signal is emitted everytime print() is called

    def flush(self):
        pass

#
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #os.putenv("QT_SCALE_FACTOR","1.8")
    myapp = StartQT5()
    myapp.show()
    # # sys.stderr = OutLog(myapp.ui.textBrowser, sys.stderr)
    # # sys.stdout = OutLog(myapp.ui.textBrowser, sys.stdout)
    # # sys.stdout = EmittingStream()
    sys.stdout = EmittingStream(textWritten=myapp.normalOutputWritten)
    # # print() calls sys.stdout.write(), which here directs to EmittingStream.write().
    # # It is also possible to connect signals by passing a slot as a keyword argument corresponding to the name of the signal when creating an object, or using the pyqtConfigure() method of QObject. https://www.riverbankcomputing.com/static/Docs/PyQt4/new_style_signals_slots.html#connecting-signals-using-keyword-arguments
    # # logging.basicConfig(format="%(message)s",level=logging.INFO,stream=sys.stdout)
    sys.exit(app.exec_())
