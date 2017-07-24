# -*- coding: utf-8 -*-
import sys
#import dollwidget
from DollUi import DollUi
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QApplication, QAction, QMainWindow, QMenuBar
from PyQt5.QtGui import QIcon
import getopt
class Example(QMainWindow):
    
    def __init__(self, usbcom=None, target='0.0.0.0', port=0):
        super(Example, self).__init__()
        self.usbcom = usbcom
        self.target = target
        self.port   = port        
        self.initUI()
        
    def initUI(self):
        self.doll     = DollUi(self.usbcom, self.target, self.port)
        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        action = fileMenu.addAction('Change File Path')
        action.triggered.connect(self.changeFilePath)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)
        self.setCentralWidget(self.doll)
        self.setWindowTitle('Doll UI')

    def changeFilePath(self):
        print('changeFilePath')
        # self.userFilePath = functions_classes.changeFilePath()
        # functions_classes.storeFilePath(self.userFilePath, 1) 
def main():
    usbcom=None
    target='0.0.0.0'
    port=0
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hu:t:p:", ["help","usbcom","target","port"])
    except getopt.GetoptError as err:
        print str(err)
    for o,a in opts:
        if o in ("-h", "--help"):
            pass
        elif o in ("-u", "--usbcom"):
            usbcom = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"                         
    app = QApplication(sys.argv)
    ex = Example(usbcom, target, port)
    ex.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
    