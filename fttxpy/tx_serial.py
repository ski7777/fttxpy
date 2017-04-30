#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import serial
import time


class TXSerial():

    def __init__(self, dev):
        self.dev = dev
        # initialize the serial connection
        self.ser = serial.Serial(self.dev)
        self.trans_lock = False

    def lockAcquire(self):
        """
        Set the communication lock
        """
        # check and wait for released lock
        while self.trans_lock:
            pass
        self.trans_lock = True

    def lockRelease(self):
        # release lock
        self.trans_lock = False

    def readToList(self):
        """
        Read all serial data to a list
        """
        # wait a moment for the data and read
        time.sleep(0.05)
        read = self.ser.read_all()
        # convert data to lines and add it to a list
        data_raw = read.splitlines()
        data = []
        for line in data_raw:
            data.append(line.decode().strip())
        return(data)

    def executeCMD(self, cmd):
        """
        Run a command on the shell and return the data
        """
        # get lock
        self.lockAcquire()
        # send data with carriage return and get data
        self.ser.write((cmd + "\r").encode())
        ser_data = self.readToList()
        self.lockRelease()
        # remove the command itself
        ser_data.pop(0)s
        return(ser_data)

    def getName(self):
        """
        get name of the TX-C
        """
        # execute CMD on TX-C
        data = self.executeCMD("type /flash/sys_par.ini")
        # grep specific line from data
        for line in data:
            if "hostname"in line:
                return(line.split("hostname = ")[1])
        return(None)

    def getVersion(self):
        """
        get TX-C Firmware version
        """
        # execute CMD on TX-C and grep data
        data = self.executeCMD("version")
        return(data[0].split("V ")[1])

    def getPrograms(self):
        """
        get programs in flash of TX-C
        """
        # execute CMD on TX-C
        data = self.executeCMD("dir /flash")
        programs = []
        # grep sepecific lines
        for line in data:
            if ".bin" in line:
                programs.append(line.split("  ")[1].split(".bin")[0])
        return(programs)

    def loadProgram(self, name):
        # the load cmd does not return anything so we don´t need the serial data
        self.executeCMD("load /flash/" + name + ".bin")
