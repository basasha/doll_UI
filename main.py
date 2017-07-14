# -*- coding: utf-8 -*-
import sys
import dollwidget
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QApplication
import getopt
class Example(QWidget):
    
    def __init__(self, usbcom=None, target='0.0.0.0', port=0):
        super(Example, self).__init__()
        self.usbcom = usbcom
        self.target = target
        self.port   = port        
        self.initUI()
        
    def initUI(self):
        self.doll     = dollwidget.DollWidget(self.usbcom, self.target, self.port)
        vbox = QVBoxLayout()
        vbox.addWidget(self.doll)
        self.setLayout(vbox)
        self.setWindowTitle('Doll UI')
        self.show()


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
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
    