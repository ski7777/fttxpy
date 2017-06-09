#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import threading
from .tx_serial import *


class ftTX():

    def __init__(self, dev):
        self.DataLock = threading.Lock()
        self.ConfigChanged = threading.Event()
        self.Data = {}

        self.X1PackageSender = 2
        self.X1PackageReciever = 1

        self.DefaultPackage = {
            "from": self.X1PackageSender,
            "to": self.X1PackageReciever,
            "TA": {},
        }
        self.connection = TXSerial(dev)

        execOK = self.openConnection()
        if not execOK:
            print("Could not connect to TX-Controller!")
            return(False)
        self.Thread = self.KeepConnectionThread(self)
        self.Thread.setDaemon(True)
        self.Thread.start()
        return(True)

    def createTA(self, ta):
        newTA = {}
        newTA["ioConfig"] = {}
        newTA["InputData"] = []
        for _ in range(8):
            newTA["InputData"].append(0)
        newTA["OutputData"] = []
        for _ in range(8):
            newTA["OutputData"].append({})
        newTA["meta"] = {}
        self.DataLock.acquire()
        self.Data[ta] = newTA
        self.DataLock.release()

    def getName(self, TXn=0):
        """
        get name of the TX-C
        """
        return(self.Data[TXn]["meta"]["name"])

    def getVersion(self, TXn=0):
        """
        get TX-C Firmware version
        """
        return(self.Data[TXn]["meta"]["ver"])

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
        # print(retData)
        if not execOK:
            return(False)
        procOK = x1Recv[retData["CC"]](self, retData)
        if not procOK:
            return(False)
        return(True)

    def openConnection(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["echo"]
        execOK = self.executeX1(data)
        if not execOK:
            return(False)
        print("x")
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["info"]
        data["TA"][0] = bytearray([])
        execOK = self.executeX1(data)
        if not execOK:
            return(False)
        return(True)

    def exchangeData(self):
        print("Data!")
        time.sleep(2)
        return(True)

    def exchangeConfig(self):
        return(True)

    def X1InfoReply(self, data):
        for TAn, TAd in data["TA"].items():
            print(len(TAd))
            name = TAd[0:17]
            while True:
                if name[len(name) - 1] == 0x00:
                    name = name[:len(name) - 1]
                else:
                    break
            addr = TAd[17:34]
            ver = str(TAd[54]) + "." + str(TAd[55])
            if not TAn in self.Data.keys():
                self.createTA(TAn)
            self.DataLock.acquire()
            self.Data[TAn]["meta"]["name"] = name.decode("utf-8")
            self.Data[TAn]["meta"]["addr"] = addr.decode("utf-8")
            self.Data[TAn]["meta"]["ver"] = ver
            self.DataLock.release()
        return(True)

    class KeepConnectionThread(threading.Thread):

        def __init__(self, parent):
            threading.Thread.__init__(self)
            self.parent = parent
            self.stopEvent = threading.Event()

        def run(self):
            while not self.stopEvent.isSet():
                # Every failing serial Communication will trigger:
                # self.stopThread()
                if self.parent.ConfigChanged.isSet():
                    runOK = self.parent.exchangeConfig
                    if not runOK:
                        self.stopThread()
                        break
                runOK = self.parent.exchangeData()
                if not runOK:
                    self.stopThread()
                    break

        def stopThread(self):
            self.stopEvent.set()
            print("Connection to the TX-Controller has been lost!")

from .CommandCodes import x1Recv, x1Send
