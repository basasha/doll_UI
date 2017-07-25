# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QGraphicsItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QDialog, QHBoxLayout,
    QApplication, QGraphicsTextItem)
from PyQt5.QtCore import QPointF
import sys
'''
2017/07/25 15:39 create by basasha 
'''
#timeUnit  = 0.05
timeFactor = 20 #(timeFactor = 1 / timeUnit )

class QGraphicsTimeline(QGraphicsView):
    def __init__(self, scale=False, emotionPool=None):
        super(QGraphicsTimeline, self).__init__()
        self.scale = scale
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.timeBlock =TimeBlock(None,length=20)
        self.scene.addItem(self.timeBlock)



    def setSize(self, w, h):
        pass

    def setValue(self, value):
        self.value = value
            
class TimeBlock(QGraphicsRectItem):
    """docstring for  TimeBlock"""
    '''
            data type: "00000001@1\n"
            8 char as simple time stamp (time unit: 50ms)
            maximum time (10^8-1)/20 s >= 5 * 10^6 s > 1300 hr        
            1 char as control bit
    '''
    def __init__(self, parent=None, length=1, emotionPool=None, xPos=0):
        super(TimeBlock, self).__init__(parent)
        self.length      = length
        self.emotionPool = emotionPool
        self.xPos        = xPos
        if self.emotionPool:self.paintBlock()
        else:self.paintScale()

    def paintScale(self):
        times  = self.length * timeFactor
        region = self.boundingRect()
        width  = region.width()
        height = region.height()
        pos    = region.topLeft() 
        for i in range(0, times):
            t1 = QGraphicsTextItem('|', self)
            t1.setPos(pos)
            
            t2 = QGraphicsTextItem('{}'.format(i+int(self.xPos)), self)
            t2.setPos(t1.bottomLeft())

            pos.setX(pos.x() + int(width / times))


    def paintBlock(self):
        pass

class MainFrame(QDialog):
    def __init__(self, parent = None):
        super(MainFrame, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.addWidget(QGraphicsTimeline())
        self.setWindowTitle("Basic test")

def main():                      
    app = QApplication(sys.argv)
    ex = MainFrame()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
