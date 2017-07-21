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
here in component by DollWidget
   v1           
|-----------------|  
| Play| Stop| Re. |                                                            
|-----------------|  |-------------------------------------------------| <-----------             
|-|.    Doll1.   _|  |0    5    10    15     20    25    30    35    40| <--- h1    |
|               |+|  |-------------------------------------------------|            |
|               |-|  |-------------------------------------------------|            |---- v2
|               |+|  |-------------------------------------------------|            |
|_______________|+|  |-------------------------------------------------| <-----------
||
||
||
||
||
||
//------------------------------------------------------------------------//
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
取得初始條件
以現在條件來做換算

update傳給timeline需要的數據
現在時間刻度（紅色）
現在錄製方塊
錄製方塊包括方塊時間，方塊數據

//------------------------------------------------------------------------//
本日問題：
由於self.time每次都是從０開始記數，因此，如果一開始先動到時間刻度，他並不會按照時間刻度的位置開始。
反而是從０開始，這不是我們要的
但是又不能簡單地寫於slider的valuechange內，因為會跟一般時間刻度再跑的時候衝突
//------------------------------------------------------------------------//
'''
class DollWidget(QWidget):
    def __init__(self, usbcom=None, target='0.0.0.0', port=0, name='Uno_Doll'):
        super(DollWidget, self).__init__()
        self.name   = name
        self.usbcom = usbcom
        self.target = target
        self.port   = port
        self.sock   = None
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

'''
-------------------------------------------------------------------------------------
timeline 引入資料
１．時間線
２．資料
-------------------------------------------------------------------------------------
timeline 所需資料
１．資料池？單純存於程式當中只要沒有overflow，優點是方便存取，缺點是記憶體負擔沈重
２．暫存檔？優點是記憶體負擔輕，缺點是不方便存取（尤其當使用者有大量資料時，尋找時間會變得很久）
-------------------------------------------------------------------------------------
timeline 資料結構
1. we need initial value of the doll
2. when we get data, calculus and show it on UI
above statement, we might calculus first then send a value to TimeLine
-------------------------------------------------------------------------------------
timeLine 繪製問題
1.由於僅是一堆線條繪製而成，需要另外再加入１個時間基準線以供移動
2.無法直接移動一塊表情块，所以無法實現即時複製及搬運
3.由於UI的時間刻度目前是以區域變數控制，所以repaint時，會讓時間刻度跑掉
4.目前沒有直接從程式就能觀察到表情的功能，所以不知當下錄製的表情块，不夠直觀
5. 自製表情池，直接從表情池讀出目前需要顯示的那段為什麽
6.以上所有問題皆能透過重載timeline的QMouseEvent來達到需求
'''

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



    def getEmotiomFromPool(self):   
        if self.value > 10:
            #upper = self.value + 2
            lower = self.value - 10
        else:
            lower = 0 #upper = 11
        self.emotionPool.seek(lower * 75)
        for i in range(0,200):    
            pass
'''
2017/07/07 13:36-17:45
2017/07/10 13:32-18:15
2017/07/12 13:30-17:05
2017/07/14 13:20-16:00
2017/07/17 13:48-16:10
2017/07/19 14:26-17:10
2017/07/21 13:40-16:38 fin
這是一個備份檔，最後編輯2017/07/21 16:38
'''