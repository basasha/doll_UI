# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QGraphicsItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QDialog, QHBoxLayout,
    QApplication, QGraphicsTextItem)
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPen, QPainter, QFont
import sys
'''
2017/07/25 15:39 create by basasha 
'''
#timeUnit  = 0.05
timeFactor = 20 #(timeFactor = 1 / timeUnit )

class QGraphicsTimeline(QGraphicsView):
    def __init__(self, scale=False, emotionPool=None):
        super(QGraphicsTimeline, self).__init__()
        #self.setAcceptDrops(True)
        self.scale = scale
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 700, 700)
        #self.timeBlock =TimeBlock(None,length=20)
        #self.scene.addItem(self.timeBlock)
        self.timeScale = TimeScale(None, 50, 50)
        #self.timeScale.setDragEnabled(True)
        self.scene.addItem(self.timeScale)
        self.currentDraggedItem = None

    def setSize(self, w, h):
        pass

    def setValue(self, value):
        self.value = value

    
    def mousePressEvent(self, event):
        self.currentDraggedItem = self.itemAt(event.pos())
        super(QGraphicsTimeline, self).mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if not self.currentDraggedItem is None:
            c = self.currentDraggedItem
            p = c.parentItem()
            while p:
                c=p
                p=c.parentItem()
            c.setPos(event.pos())
        super(QGraphicsTimeline, self).mouseReleaseEvent(event)



class TimeBlock(QGraphicsRectItem):
    """docstring for  TimeBlock"""
    '''
            data type: "00000001@1\n"
            8 char as simple time stamp (time unit: 50ms)
            maximum time (10^8-1)/20 s >= 5 * 10^6 s > 1300 hr        
            1 char as control bit
    '''
    def __init__(self, parent=None, x=0, y=0, w=1, h=1):
        super(TimeBlock, self).__init__(parent)
        self.w  = w  if w>50 else 50 # minimum width  = 50
        self.h = h if h>50 else 50  # minimum height = 50
        self.emotionPool =None
    @classmethod
    def fromPath(cls, path):
        cls.emotionPool = path


    def paintBlock(self):
        if not self.emotionPool is None:
            qp =QPainter()
            qp.begin(self)
            font = QFont('Serif', 8, QFont.Light)
            qp.setFont(font)               
            step = int(self.w / timeFactor)
            for i in range(0, timeFactor):
                s = self.emotionPool.readline()
                if '\n' in s and '@' in s: 
                    lists =s.replace('\n', '').spilt('@')
                    u = int(lists[1])// 3
                    d = int(lists[1]) - 3 * u
                    u=u*0.05*self.h+0.6*self.h
                    d=d*0.05*self.h+0.1*self.h
                    qp.drawLine(int(i * self.w / timeFactor)-1,u,int(i * self.w  /timeFactor),u)
                    qp.drawLine(int(i * self.w / timeFactor)-1,d,int(i * self.w / timeFactor),d)
                    



class TimeScale(QGraphicsRectItem):
    #作為時間刻度使用 ㄧ條刻度線需要建構子有 位置，起始值
    #目前長度固定為20秒
    #但是希望長度能彈性的調整
    def __init__(self, parent=None, x=0, y=0, start=0):
        super(TimeScale, self).__init__(parent)
        self.length = timeFactor
        self.w      = 500
        self.h      = 30
        self.x      = x
        self.y      = y
        self.start  = start
        self.baseline = 0
        #self.dragged =False
        self.drawScale()
    @classmethod
    def reSize(cls, w, h):
        cls.setSize(w, h)

    def setSize(self, w, h):    
        self.w = w
        self.h = h
    #為美好的時間刻度線上刻痕

    def setBaseLine(self, b):
        self.baseline = b

    def drawScale(self):
        
        pos = QPointF(self.x, self.y)

        for i in range(0, self.length):#每一秒有1個刻度，總共 length 秒
            t1 = QGraphicsTextItem('|', self)
            t1.setDefaultTextColor(QColor(Qt.blue))
            t1.setPos(pos)
            
            t2 = QGraphicsTextItem('{}'.format(i+int(self.start)), self)
            t2.setDefaultTextColor(QColor(Qt.blue))
            t2.setPos(t1.boundingRect().bottomLeft()+pos)

            pos.setX(pos.x() + int(self.w/ self.length))
        self.setRect(50,50,self.w, self.h)
  



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
'''
2017/07/26 13:58-

'''