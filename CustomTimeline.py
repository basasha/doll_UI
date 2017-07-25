# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication, QLabel, QCheckBox, QPushButton, QGridLayout, QScrollArea, QScrollBar,
    QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QMouseEvent
import serial
import threading
import dollcmd
import time
'''
UDP_IP = "192.168.4.1"
UDP_PORT = 6000
sock =''
'''
class  Communicate(QObject):

    updateDW =pyqtSignal(int)

'''
Record Mode:

Input (usb comm port) -> handleIO -> calculus -> Output (UDP)
                                         |-----> set value to TimeLine -> update UI
                                         |-----> save data to dynamic qbe data file

Play   Mode:

Input (dynamic qbe data file) -> handleIO -> calculus -> Output (UDP)
                                                 |-----> set value to TimeLine -> update UI
                                                 |-----> save data to dynamic qbe data file
//------------------------------------------------------------------------//
file type:

.sqbe : emotion setting file
.dqbe : dynamic emotion file
.qbe  : combination of .sqbe and .dqbe
//------------------------------------------------------------------------//
'''
'''
新版ＵＩ
 ______________________________________________________________________________
|______________________________________________________________________________|
|(-)Doll1 >>|(-)eye     |          o o       o o                               |
|-----------|-----------|            o o o o o        o o           o o        |
|(-)Doll2  >|(-)eyebrow |            o       o          o  o o o o o           |
|-----------|-----------|           o   O  O  o          o   \   /  o          |
|(-)Doll3  >|(-)eye     |           o     |   o          o   0   0  o          |
|-----------|-----------|             o  --   o           o    |   o           |
|(+)        |(-)mouse   |               o  o                o / \ o            |
|-----------|-----------|                                     o o              |
|           |(-)sound   |                                                      |
|-----------|-----------|               no event                               |
|           |           |                                                      |
|-----------|-----------|                                                      |
|     DoubleClickEvent  |                                                      |
|-----------------------|------------------------------------------------------|
|                       |     _ --_     _ ----   --      -     ___  -   --     |
|                       | _ --      _ --       --  --____ _____   --  -    - - |
|                       |------------------------------------------------------|                                                      |
|                       | drag event and drop event and click event            |
|                       |                                                      |
|                       |------------------------------------------------------|                                                      |
|                       |                                                      |
|                       |                                                      |
|                       |------------------------------------------------------|                                                      |
|                       |                                                      |
|                       |                                                      |
|                       |------------------------------------------------------|                                                      |
|                       |                                                      |
|                       |                                                      |
|                       |------------------------------------------------------|                                                      |
|                       |                                                      |
|                       |                                                      |
|                       |------------------------------------------------------|                                                      |
|                       |                                                      |
|                       |                                                      |
|_______________________|______________________________________________________|

'''
class DollWidget(QWidget):
    def __init__(self, usbcom=None, target='0.0.0.0', port=0, name='Uno_Doll'):
        super(DollWidget, self).__init__()
        self.name   = name
        self.usbcom = usbcom
        self.target = target
        self.port   = port
        self.initUI()

    def setName(self, name):
        self.name = name

    def setValue(self, value):
        self.timeline.setValue(value)
        self.eyebrowLine.setValue(value)
        self.eyeLine.setValue(value)
        self.earLine.setValue(value)
        self.mouseLine.setValue(value)

    def setSlider(self, value):
        if value > 0.8 * self.relativeMaximum:
            self.relativeMaximum = 1.2*self.relativeMaximum
        self.slider.setValue(int(100*value/self.relativeMaximum))

    def initUI(self):
        self.mode        = 0
        self.time        = 0
        self.eyebrowEmotion = open('eyebrow.dqbe','w+')
        self.eyeEmotion = open('eye.dqbe','w+') 
        self.earEmotion = open('ear.dqbe','w+') 
        self.mouseEmotion = open('mouse.dqbe','w+')
        self.file        = open('emoji.dqpe','a+')  
        '''mode 1 as play. mode 2 as record. mode 3 as stop. mode 4 as save.'''
        self.thisDoll    = QCheckBox(self.name, self)
        self.eyebrow     = QCheckBox('eyebrow', self)
        self.eye         = QCheckBox('eye', self)
        self.ear         = QCheckBox('ear', self)
        self.mouse       = QCheckBox('mouse', self)
        self.playBtn     = QPushButton('Play', self)
        self.recordBtn   = QPushButton('Record', self) 
        self.stopBtn     = QPushButton('Stop', self)
        self.saveBtn     = QPushButton('Save', self)
        self.timeline    = TimeLine(scale=True)
        self.eyebrowLine = TimeLine(scale=False, emotionPool=self.eyebrowEmotion, types='eyebrow')
        self.eyeLine     = TimeLine(scale=False, emotionPool=self.eyeEmotion, types='eye')
        self.earLine     = TimeLine(scale=False, emotionPool=self.earEmotion, types='ear')
        self.mouseLine   = TimeLine(scale=False, emotionPool=self.mouseEmotion, types='mouse')
        self.slider      = QScrollBar(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.relativeMaximum = 15
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.valueChange)

        self.playBtn.clicked.connect(self.handlePlayBtn)
        self.stopBtn.clicked.connect(self.handleStopBtn)
        self.recordBtn.clicked.connect(self.handleRecordBtn)
        self.saveBtn.clicked.connect(self.handleSaveBtn)
        self.thisDoll.stateChanged.connect(lambda:self.handleCheck(self.thisDoll))

        dollcmd.setComPort(self.usbcom)

        #UI
        layout           = QGridLayout(self)
        layout.addWidget(self.playBtn, 0,0,1,1)
        layout.addWidget(self.recordBtn, 0,1,1,1)
        layout.addWidget(self.stopBtn, 0,2,1,1)
        layout.addWidget(self.saveBtn,0,3,1,1)

        layout.addWidget(self.thisDoll, 1,0,1,1)
        layout.addWidget(self.eyebrow, 2,1,1,1)
        layout.addWidget(self.eye, 3,1,1,1)
        layout.addWidget(self.ear, 4,1,1,1)
        layout.addWidget(self.mouse, 5,1,1,1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scrollContent = QWidget(scroll)

        scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollContent.setLayout(scrollLayout)
        scrollLayout.addWidget(self.timeline)
        scrollLayout.addWidget(self.eyebrowLine)
        scrollLayout.addWidget(self.eyeLine)
        scrollLayout.addWidget(self.earLine)
        scrollLayout.addWidget(self.mouseLine)
        scroll.setWidget(self.scrollContent)
        layout.addWidget(self.slider,0,4,1,7)
        layout.addWidget(self.scrollContent, 1,4,5,7)
        self.show()

    def valueChange(self):
        s = self.slider.value()
        value = (s * self.relativeMaximum *0.01)
        self.setValue(value)
        if self.mode != 1 and self.mode!=2 and self.mode!=4:
            self.time = value * 20  
    def handleCheck(self, this):
        if this.isChecked():
            state = Qt.Checked
        else:
            state = Qt.Unchecked    
        self.eye.setCheckState(state)
        self.eyebrow.setCheckState(state)
        self.ear.setCheckState(state)
        self.mouse.setCheckState(state)

    def handlePlayBtn(self):
        self.mode = 1
        self.handleIO()

    def handleStopBtn(self):
        self.mode = 3
        
    def handleRecordBtn(self):
        self.mode = 2
        self.handleIO()

    def handleSaveBtn(self):    
        self.mode = 4
        self.handleIO()
        '''
        eyebrow and eye 
        jd1[0] 1023 = left, 0 = right
        jd1[1] 1023 = up. , 0 = down

        ear
        1023. = up, 0 = down

        '''
    def handleIO(self):
        if self.mode == 1 :
            data = self.file.readline()
            #dollcmd.sendUDP()
            self.time += 1
            self.setValue(self.time * 0.05)
            self.setSlider(self.time *0.05)
            QTimer.singleShot(50, self.handleIO)
        if self.mode == 2 :
            data = dollcmd.handleIOData()
            self.file.write(data)
            #dollcmd.sendUDP(data)
            if '\n' in data :
                lists = data.replace('\n','').split(',')
                #ear
                if int(lists[0]) > 512:i = 0
                else: i = 1
                i *= 3
                if int(lists[1]) > 512:i += 0
                else: i += 1   
                self.earEmotion.write('{}@{}\n'.format(str(self.time).zfill(8), str(i)))
                #ear
                #eyebrow
                if int(lists[2]) > 682: i = 0
                elif int(lists[2]) > 341: i = 1
                else: i = 2
                i *= 3
                if int(lists[3]) > 682: i += 0
                elif int(lists[3]) > 341: i += 1
                else: i += 2  
                self.eyebrowEmotion.write('{}@{}\n'.format(str(self.time).zfill(8), str(i)))
                #eyebrow
                #eye
                if int(lists[6]) > 682: i = 0
                elif int(lists[6]) > 341: i = 1
                else: i = 2
                i *= 3
                if int(lists[7]) > 682: i += 0
                elif int(lists[7]) > 341: i += 1
                else: i += 2  
                self.eyeEmotion.write('{}@{}\n'.format(str(self.time).zfill(8), str(i)))
                #eye
                #mouse
                if int(lists[10]) > 682: i = 0
                elif int(lists[10]) > 341: i = 1
                else: i = 2
                i *= 3
                if int(lists[11]) > 682: i += 0
                elif int(lists[11]) > 341: i += 1
                else: i += 2  
                self.mouseEmotion.write('{}@{}\n'.format(str(self.time).zfill(8), str(i)))
                #mouse
            self.time  += 1
            self.setValue(self.time * 0.05)
            self.setSlider(self.time *0.05)
            QTimer.singleShot(50, self.handleIO)
        if self.mode == 3 :
            pass
        if self.mode == 4 :
            pass

    def mousePressEvent(self, event):
        pass
    def mouseMoveEvent(self,event):
        pass
class TimeLine(QWidget):
    def __init__(self, scale=False, emotionPool=None, types=''):
        super(TimeLine, self).__init__()
        self.scale = scale
        self.initUI()
        self.emotionPool = emotionPool
        self.types = types
    def initUI(self):
        self.value = 0
        if self.scale:
            self.setMinimumSize(500,20)
        else:    
            self.setMinimumSize(500,60)

    def setValue(self, value):
        self.value = value
        self.repaint()

    def paintEvent(self, e):
        qp =QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        font = QFont('Serif', 8, QFont.Light)
        qp.setFont(font)

        size = self.size()
        w = size.width()
        h = size.height()
        step = int(round(w/12.0))

        qp.drawRect(0,0,w,h)
        qp.setPen(QColor(231, 221, 218))
        qp.setBrush(QColor(231, 221, 218))  
        for i in range(0, w, int(round(step/20.0))):
            qp.drawLine(i,1,i,h)

        j = 0
        correction_word = 1
        correction_time = 0
        '''從表情池讀取表情，並根據目前的時間刻度繪製表情'''
        '''
        每一軌表情分 上中下 跟 左中右 共９種組合，所以用一個char來計數
        上＝左＝０，中＝１，下＝右＝２
        前一組的上中下會乘上基底３
        e.g. 7 / 3 = 2 ... 1
                 |   |     |
                 ˇ   ˇ     ˇ 
               基底 代表下  代表中
        組合起來就代表中下       
        首先需判斷目前顯示是哪一段時間區段，並根據時間區段從表情池撈出不同的表情块來顯示於UI
        '''
        qp.setPen(QColor(0, 138, 92))
        qp.setBrush(QColor(0, 138, 92))  
        if self.value > 10:
            lower = self.value - 10
        else:
            lower = 0 #upper = 11
        if self.emotionPool:
            self.emotionPool.seek(lower * 20 * 11)
            for i in range(0,240):    
                s = self.emotionPool.readline()
                if '@' in s: 
                    lists = s.split('@')
                    u = int(lists[1])// 3
                    d = int(lists[1]) - 3 * u
                    u=u*0.05*h+0.6*h
                    d=d*0.05*h+0.1*h
                    qp.drawLine(int(i * w / 240)-1,u,int(i * w  /240),u)
                    qp.drawLine(int(i * w / 240)-1,d,int(i * w / 240),d)
                    
                else:
                    break

        '''從表情池讀取表情，並根據目前的時間刻度繪製表情'''
        qp.setPen(QColor(255, 175, 175))
        qp.setBrush(QColor(255, 175, 175))       
        if self.value > 10:
            correction_time = int((self.value-int(self.value)) * step)
            correction_word = int(self.value) - 9
            qp.drawLine(10 * step,0, 10 * step, h)            
        else:
            qp.drawLine(self.value * step,0, self.value * step, h)  
        qp.setPen(QColor(0, 0, 0))
        qp.setBrush(QColor(0, 0, 0))                
        for i in range(step-correction_time, 12*step, step):
            
            qp.drawLine(i, 0, i, 5)
            metrics = qp.fontMetrics()
            fw = metrics.width(str(j+correction_word))
            if self.scale:
                qp.drawText(i-fw/2, h/2, str(j+correction_word))
            j = j + 1

'''
2017/07/07 13:36-17:45
2017/07/10 13:32-18:15
2017/07/12 13:30-17:05
2017/07/14 13:20-16:00
2017/07/17 13:48-16:10
2017/07/19 14:26-17:10
2017/07/21 13:40-16:38
2017/07/25 13:34:-
'''