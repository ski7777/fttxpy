#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import serial
import time


class TXSerial():

    def __init__(self, dev):
        self.dev = dev
        self.ser = serial.Serial(self.dev)
        self.trans_lock = False

    def lockAcquire(self):
        self.trans_lock = True

    def lockRelease(self):
        self.trans_lock = False

    def checkLocked(self):
        return(self.trans_lock)

    def readToList(self):
        time.sleep(0.1)
        read = self.ser.read_all()
        data_raw = read.splitlines()
        data = []
        for line in data_raw:
            data.append(line.decode().strip())
        return(data)

    def executeCMD(self, cmd):
        while self.checkLocked():
            pass
        self.lockAcquire()
        self.ser.write((cmd + "\r").encode())
        ser_data = self.readToList()
        ser_data.pop(0)
        self.lockRelease()
        return(ser_data)

    def getName(self):
        data = self.executeCMD("type /flash/sys_par.ini")
        for line in data:
            if "hostname"in line:
                return(line.split("hostname = ")[1])
        return(None)

    def getVersion(self):
        data = self.executeCMD("version")
        return(data[0].split("V ")[1])
