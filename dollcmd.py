# -*- coding: utf-8 -*-
import socket
import serial
import threading
import getopt
import sys
import time
port = 0
buffer_size = 1024
usbcom =''
target =''
sysnc = False
init =[0, 0, 545, 570, 555, 525, 580, 500, 555, 525, 0, 0, 0]
dic={}
f = open('emotionSetting.sqbe', 'a+')
f.close()
f = open('emotionSetting.sqbe', 'r+')
led =['0','0','0','0']
s_com = ''
sock=''
last_data = ''
holdon = False
quick_flag = False
'''
keyboard 0,0,0,0            // 快速鍵 //最高權限
svr 887,1023,643,631,728   //  多工器輸出，由GUI導向某個硬體設備
JD1 534,563                   // 搖桿
JD2 551,521
JD3 580,501
JD4 558,523
JD5 539,531
BT 0,0,0,0,0,0                //按鈕

輸出格式：左耳 右耳 左眉上下 左眉左右 右眉上下 右眉左右 左眼上下 左眼左右 右眼上下 右眼左右 左嘴角 右嘴角 嘴巴開闔 
        svr1 svr2 JD1[0] JD1[1]   JD2[0] JD2[1]  JD3[0]  JD3[1]  JD4[0]  JD4[1] JD5[0] JD5[1]  BT[0]
init = [0,0,545,570,555,525,580,500,555,525,0,0,0]
'''
def prepareUDP():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def sendUDP(sendData):
    global sock
    UDP_IP = "192.168.4.1"
    UDP_PORT = 6000
    sock.sendto(sendData, (UDP_IP, UDP_PORT))

def handleIOData():
    global sysnc
    global dic
    global f
    global led
    global s_com
    global last_data
    global holdon
    global init
    global quick_flag
    #s= serial.Serial(port = usbcom, baudrate = 115200)
    #s_com = serial.Serial(port = usbcom, baudrate = 115200)
    s=s_com
    #loadSetting()
    key = []
    jd1 = []
    jd2 = []
    jd3 = []
    jd4 = []
    jd5 = []
    bt  = []
    svr = []
    

    sendData = last_data
    t =time.time()
    s.flushInput()
    data = s.readline()  #這裡基本上延遲約50-60ms
    while not (('keyboard' in data) and ('svr' in data) and ('BT' in data) and ('\n' in data)):
        data  = s.readline()
    #print data
    #print '\n'
    data      = data.replace('\n','')
    datalist  = data.split(' ')
    #print 'it cost {} seconds to get data\n'.format(time.time()-t)
    #print key
    #print '\n'
    t=time.time()
    for i in range(0, len(datalist)):
        if 'keyboard' in datalist[i]:
            key = datalist[i+1].split(',')
        if 'JD' in datalist[i]:
            if '1' in datalist[i]: jd1 = datalist[i+1].split(',')
            if '2' in datalist[i]: jd2 = datalist[i+1].split(',')
            if '3' in datalist[i]: jd3 = datalist[i+1].split(',')
            if '4' in datalist[i]: jd4 = datalist[i+1].split(',')
            if '5' in datalist[i]: jd5 = datalist[i+1].split(',')
        if 'BT' in datalist[i]:
            bt = datalist[i+1].split(',')
        if 'svr' in datalist[i]:
            svr = datalist[i+1].split(',')

            jd1 = [item.zfill(4) for item in jd1]
            jd2 = [item.zfill(4) for item in jd2]
            jd3 = [item.zfill(4) for item in jd3]
            jd4 = [item.zfill(4) for item in jd4]
            jd5 = [item.zfill(4) for item in jd5]

            bt  = [item.zfill(4) for item in bt]
            svr = [item.zfill(4) for item in svr]

    key_value = 0 
        #將key的值轉為十進制
    for i in key:
        key_value *= 16
        key_value += int(i, 16)
    if key_value > 0:

        if int(key[2], 16) & 0x2000 :
            holdon = not holdon

        elif int(key[2], 16) & 0x1000 :

            sysnc = not sysnc
        else:
            if holdon:
                dic[key_value] = sendData
                f.write('{},{},{},{}\t{}'.format(key[0].zfill(4), key[1].zfill(4), key[2].zfill(4), key[3].zfill(4), sendData))
                holdon = not holdon
                if   int(key[0], 16)>0:led[0] = hex(int(led[0], 16) | int (key[0], 16)).replace('0x', '')
                elif int(key[1], 16)>0:led[1] = hex(int(led[1], 16) | int (key[1], 16)).replace('0x', '')
                elif int(key[2], 16)>0:led[2] = hex(int(led[2], 16) | int (key[2], 16)).replace('0x', '')
                elif int(key[3], 16)>0:led[3] = hex(int(led[3], 16) | int (key[3], 16)).replace('0x', '')
            else:
                if dic.get(key_value):
                    sendData  = str(dic.get(key_value))
                    last_data = sendData
                    quick_flag =True

        if holdon:
            led[2] =hex(int(led[2], 16) | 0x2000).replace('0x', '')
        else:
            led[2] =hex(int(led[2], 16) & 0xDFFF).replace('0x', '')
        if sysnc:
            led[2] =hex(int(led[2], 16) | 0x1000).replace('0x', '')
        else:
            led[2] =hex(int(led[2], 16) & 0xEFFF).replace('0x', '')
        
        s.write('{},{},{},{}\n'.format(led[0], led[1], led[2], led[3]))               
    
    elif holdon:
        pass        
    else:
        t1 = [svr[2], svr[1], jd1[0], jd1[1], jd2[0], jd2[1], jd3[0], jd3[1], jd4[0], jd4[1], svr[3], svr[4], bt[0]]

        if isInit(t1, init) and quick_flag:
            pass
        elif not sysnc:
            sendData = '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(svr[2], svr[1], jd3[0], jd3[1], jd3[0], jd3[1], jd4[0], jd4[1], jd4[0], jd4[1], jd5[1], jd5[1], bt[0])
            last_data = sendData
            quick_flag =False
        else:
            sendData = '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(svr[2], svr[1], jd1[0], jd1[1], jd2[0], jd2[1], jd3[0], jd3[1], jd4[0], jd4[1], svr[3], svr[4], bt[0])
            last_data = sendData
            quick_flag =False
    return sendData

def isInit(target, init):
    if len(target) == len(init):
        for i in range(0, len(target)):
            if abs(int(init[i])-int(target[i])) > 70:
                return False
    else:
        return False
    return True             
                
def setComPort(c):
    #global usbcom
    #usbcom = c
    global s_com
    s_com = serial.Serial(port = c, baudrate = 115200)
    loadSetting()
    prepareUDP()
def loadSetting():
    global f
    global dic
    global led
    global s_com
    f.seek(0)
    while 1:
        r =f.readline()
        if len(r):
            #r = r.replace('\n','')
            datalist = r.split('\t')
            key = datalist[0].split(',')
            key_value = 0 
            #將key的值轉為十六進制
            for i in key:
                key_value *= 16
                key_value += int(i, 16)
            dic[key_value] = datalist[1]
            if   int(key[0], 16)>0:led[0] = hex(int(led[0], 16) | int (key[0], 16)).replace('0x', '')
            elif int(key[1], 16)>0:led[1] = hex(int(led[1], 16) | int (key[1], 16)).replace('0x', '')
            elif int(key[2], 16)>0:led[2] = hex(int(led[2], 16) | int (key[2], 16)).replace('0x', '')
            elif int(key[3], 16)>0:led[3] = hex(int(led[3], 16) | int (key[3], 16)).replace('0x', '')   
            print 'loadSetting success-----------------***********************'
        else:break   
    s_com.write('{},{},{},{}\n'.format(led[0], led[1], led[2], led[3]))