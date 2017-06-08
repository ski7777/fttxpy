#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import threading
from .tx_serial import *


class ftTX():

    def __init__(self, dev):
        self.DataLock = threading.Lock()
        self.Data = {}

        self.X1PackageSender = 2
        self.X1PackageReciever = 1

        self.DefaultPackage = {
            "from": self.X1PackageSender,
            "to": self.X1PackageReciever,
            "TA": {},
        }
        self.connection = TXSerial(dev)

        self.Thread = self.KeepConnectionThread(self)
        self.Thread.setDaemon(True)
        self.Thread.start()

    def createTA(self, ta):
        newTA = {}
        newTA["ioConfig"] = {}
        newTA["InputData"] = []
        for _ in range(8):
            newTA["InputData"].append(0)
        newTA["OutputData"] = []
        for _ in range(8):
            newTA["OutputData"].append({})

        self.DataLock.acquire()
        self.Data[ta] = newTA
        self.DataLock.release()

    def getName(self):
        """
        get name of the TX-C
        """
        # execute CMD on TX-C
        data = self.connection.executeCMD("type /flash/sys_par.ini")
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
        data = self.connection.executeCMD("version")
        return(data[0].split("V ")[1])

    def getPrograms(self):
        """
        get programs in flash of TX-C
        """
        # execute CMD on TX-C
        data = self.connection.executeCMD("dir /flash")
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
        self.connection.executeCMD("load /flash/" + name + ".bin")

    def runProgram(self):
        """
        Run a loaded program
        """
        # execute CMD on TX-C
        # the run cmd does not return anything so we don´t need the serial data
        self.connection.executeCMD("run")

    def stopProgram(self):
        """
        Stop a running program
        """
        # execute CMD on TX-C
        # the stop cmd does not return anything so we don´t need the serial data
        self.connection.executeCMD("stop")

    def executeX1(self, data):
        execOK, retData = self.connection.X1CMD(data)
        if not execOK:
            return(False)
        procOK = x1Recv[retData["CC"]](self, retData)
        if not procOK:
            return(False)
        return(True)

    def openConnection(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["echo"]
        return(self.executeX1(data))

    class KeepConnectionThread(threading.Thread):

        def __init__(self, parent):
            threading.Thread.__init__(self)
            self.parent = parent
            self.stopEvent = threading.Event()

        def run(self):
            while not self.stopEvent.isSet():
                #Every failing serial Communication will trigger:
                #self.stopThread()
                pass

        def stopThread(self):
            self.stopEvent.set()
            print("Connection to the TX-Controller has been lost!")

from .CommandCodes import x1Recv, x1Send
