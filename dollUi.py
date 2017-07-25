# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication, QLabel, QCheckBox, QPushButton, QGridLayout, QScrollArea, QScrollBar,
    QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QMouseEvent
import serial
import threading
import getopt
import time
from CustomTimeline import DollWidget

class  Communicate(QObject):

    updateDW =pyqtSignal(int)

class DollUi(QWidget):
    """docstring for DollUi"""
    def __init__(self, usbcom=None, target='0.0.0.0', port=0):
        super(DollUi, self).__init__()
        self.usbcom = usbcom
        self.target = target
        self.port   = port 
        self.dollItem=['eye','eyebrow','ear','mouse','sound']
        self.initUi()
    def initUi(self):    
        self.tree = QTreeWidget()
        self.dollwidget =DollWidget(self.usbcom, self.target, self.port)
        self.string = 'hello, here might be some pictures to show you how it works. Unfortunately, we haven\'t contribute that part.\n'
        self.view = QLabel(self.string,self)
        headerItem  = QTreeWidgetItem()
        item        = QTreeWidgetItem()
        for i in xrange(3):
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, "Doll {}".format(i))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in xrange(5):
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "{}".format(self.dollItem[x]))
                child.setCheckState(0, Qt.Unchecked)
        #tree.show()
        l   = QGridLayout()
        l.setColumnStretch(2,10)
        l.addWidget(self.tree,0,0,1,1)
        l.addWidget(self.view,0,10,1,10)
        v = QVBoxLayout(self)
        v.addLayout(l)
        v.addWidget(self.dollwidget)
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
    ex = DollUi(usbcom, target, port)
    ex.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
'''
2017/07/07 13:36-17:45
2017/07/10 13:32-18:15
2017/07/12 13:30-17:05
2017/07/14 13:20-16:00
2017/07/17 13:48-16:10
2017/07/19 14:26-17:10
2017/07/21 13:40-16:38
2017/07/24 13:22-18:08
2017/07/25 13:34-1
'''