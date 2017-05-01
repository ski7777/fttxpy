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

        self.X1TID = 0  # will be counted up for each package sent by the PC
        self.X1SID = 0  # will start at 0 and then set by TX-C

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

    def close(self):
        self.lockAcquire()
        self.ser.close()
        self.lockRelease()

    def reOpen(self):
        self.lockAcquire()
        self.ser.open()
        self.lockRelease()

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
        if not self.ser.isOpen():
            print("Serial communication is closed!")
            return([])
        # get lock
        self.lockAcquire()
        # send data with carriage return and get data
        self.ser.write((cmd + "\r").encode())
        ser_data = self.readToList()
        self.lockRelease()
        # remove the command itself
        ser_data.pop(0)
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
        """
        Load a program from flsh by name
        """
        # execute CMD on TX-C
        # the load cmd does not return anything so we don´t need the serial data
        self.executeCMD("load /flash/" + name + ".bin")

    def runProgram(self):
        """
        Run a loaded program
        """
        # execute CMD on TX-C
        # the run cmd does not return anything so we don´t need the serial data
        self.executeCMD("run")

    def stopProgram(self):
        """
        Stop a running program
        """
        # execute CMD on TX-C
        # the stop cmd does not return anything so we don´t need the serial data
        self.executeCMD("stop")

    def sendX1Package(self, data):
        """
        """
        return(True)

    def reciveX1Package(self):
        """
        """
        return(True, {})

    def X1CMD(slef, in_data):
        """
        send a X.1 package and return data
        """
        self.lockAcquire()
        # count the Transaction ID 1 up
        self.X1TID += 1
        # send X.1 package and get status
        ok = self.sendX1Package(in_data)
        # kill if send error
        if not ok:
            self.lockRelease()
            return(False, {})
        # recieve X.1 package and get status and data
        ok, ret_data = self.reciveX1Package()
        self.lockRelease()
        # kill if recieve error
        if not ok:
            return(False, {})
        # return ok status and data
        return(True, {})
