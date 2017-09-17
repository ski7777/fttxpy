#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import threading
import time
from .tx_serial import *


class ftTX():

    def __init__(self, dev):
        self.DataLock = threading.Lock()
        self.ConfigChanged = threading.Event()
        self.Data = {}

        self.exchangeInterval = 0.1

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
        newTA["Input"] = {}
        newTA["Input"]["Digital"] = []
        for _ in range(8):
            newTA["Input"]["Digital"].append(0)
        newTA["Input"]["Value"] = []
        for _ in range(8):
            newTA["Input"]["Value"].append(0)
        newTA["Input"]["Mode"] = []
        for _ in range(8):
            newTA["Input"]["Mode"].append(0)

        newTA["Counter"] = {}
        newTA["Counter"]["Reset"] = []
        for _ in range(4):
            newTA["Counter"]["Reset"].append(False)
        newTA["Counter"]["ResetID"] = []
        for _ in range(4):
            newTA["Counter"]["ResetID"].append(0)
        newTA["Counter"]["ResetIDTX"] = []
        for _ in range(4):
            newTA["Counter"]["ResetIDTX"].append(0)
        newTA["Counter"]["Count"] = []
        for _ in range(4):
            newTA["Counter"]["Count"].append(0)
        newTA["Counter"]["State"] = []
        for _ in range(4):
            newTA["Counter"]["State"].append(False)
        newTA["Counter"]["Mode"] = []
        for _ in range(4):
            newTA["Counter"]["Mode"].append(0)

        newTA["Output"] = {}
        newTA["Output"]["Type"] = []
        for _ in range(4):
            newTA["Output"]["Type"].append(0)
        newTA["Output"]["Duty"] = []
        for _ in range(8):
            newTA["Output"]["Duty"].append(0)
        newTA["Output"]["Sync"] = []
        for _ in range(4):
            newTA["Output"]["Sync"].append(0)
        newTA["Output"]["Distance"] = []
        for _ in range(4):
            newTA["Output"]["Distance"].append(0)
        newTA["Output"]["ID"] = []
        for _ in range(4):
            newTA["Output"]["ID"].append(0)
        newTA["Output"]["IDTX"] = []
        for _ in range(4):
            newTA["Output"]["IDTX"].append(0)

        newTA["meta"] = {}
        newTA["meta"]["name"] = ""
        newTA["meta"]["addr"] = ""
        newTA["meta"]["ver"] = ""
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
        if not execOK:
            return(False)
        procOK = x1Recv[retData["CC"]](self, retData)
        if not procOK:
            return(False)
        return(True)

    def openConnection(self):
        execOK = self.X1EchoSend()
        if not execOK:
            return(False)

        execOK = self.X1StateSend()
        if not execOK:
            return(False)

        self.createTA(0)

        execOK = self.X1InfoSend()
        if not execOK:
            return(False)
        return(True)

    def exchangeData(self):
        execOK = self.X1IOSend()
        if not execOK:
            return(False)
        return(True)

    def exchangeConfig(self):
        return(True)

    def X1EchoSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["echo"]
        execOK = self.executeX1(data)
        return(execOK)

    def X1InfoSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["info"]
        for n in self.Data.keys():
            data["TA"][n] = bytearray()
        execOK = self.executeX1(data)
        return(execOK)

    def X1IOSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["IO"]
        self.DataLock.acquire()
        for TXn, TXd in self.Data.items():
            CounterResetData = bytearray()
            for n in range(4):
                if TXd["Counter"]["Reset"][n] == True:
                    TXd["Counter"]["ResetID"][n] += 1
                    TXd["Counter"]["Reset"][n] = False
                CounterResetData = CounterResetData + TXd["Counter"]["ResetID"][n].to_bytes(2, byteorder='little')
            SyncData = bytearray()
            DutyData = bytearray()
            DistanceData = bytearray()
            MotorIDData = bytearray()
            for n in range(4):
                SyncData.append(TXd["Output"]["Sync"][n])
                for o in range(2):
                    DutyData = DutyData + TXd["Output"]["Duty"][(n * 2) + o].to_bytes(2, byteorder='little')
                DistanceData = DistanceData + TXd["Output"]["Distance"][n].to_bytes(2, byteorder='little')
                MotorIDData = MotorIDData + TXd["Output"]["ID"][n].to_bytes(2, byteorder='little')
            data["TA"][TXn] = CounterResetData + SyncData + DutyData + DistanceData + MotorIDData
        self.DataLock.release()
        execOK = self.executeX1(data)
        if not execOK:
            return(False)
        return(True)

    def X1IOReply(self, data):
        for TAn, TAd in data["TA"].items():
            self.DataLock.acquire()
            for n in range(8):
                self.Data[TAn]["Input"]["Value"][n] = int.from_bytes(TAd[2 * n:(2 * n) + 2], byteorder='little', signed=True)
            for n in range(4):
                self.Data[TAn]["Counter"]["State"][n] = not bool(TAd[16 + n])
                self.Data[TAn]["Counter"]["Count"][n] = int.from_bytes(TAd[20 + (2 * n):20 + (2 * n) + 2], byteorder='little', signed=True)
                self.Data[TAn]["Counter"]["ResetIDTX"][n] = int.from_bytes(TAd[32 + (2 * n):32 + (2 * n) + 2], byteorder='little', signed=False)
            for n in range(4):
                self.Data[TAn]["Output"]["IDTX"][n] = int.from_bytes(TAd[40 + (2 * n):40 + (2 * n) + 2], byteorder='little', signed=False)
            self.DataLock.release()
        return(True)

    def X1InfoReply(self, data):
        for TAn, TAd in data["TA"].items():
            name = TAd[0:17]
            while True:
                if name[len(name) - 1] == 0x00:
                    name = name[:len(name) - 1]
                else:
                    break
            addr = TAd[17:34]
            ver = str(TAd[54]) + "." + str(TAd[55])
            self.DataLock.acquire()
            self.Data[TAn]["meta"]["name"] = name.decode("utf-8")
            self.Data[TAn]["meta"]["addr"] = addr.decode("utf-8")
            self.Data[TAn]["meta"]["ver"] = ver
            self.DataLock.release()
        return(True)

    def X1StateSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["state"]
        data["TA"][0] = bytearray()
        execOK = self.executeX1(data)
        if not execOK:
            return(False)
        return(True)

    def X1StateReply(self, data):
        TAd = data["TA"][0]
        ExtData = TAd[0:8]
        for TXn in range(8):
            if ExtData[TXn] == 1:
                self.createTA(TXn + 1)
        return(True)

    class KeepConnectionThread(threading.Thread):

        def __init__(self, parent):
            threading.Thread.__init__(self)
            self.parent = parent
            self.stopEvent = threading.Event()

        def run(self):
            while not self.stopEvent.isSet():
                start = time.time()
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
                while time.time() - self.parent.exchangeInterval < start:
                    time.sleep(0.005)

        def stopThread(self):
            self.stopEvent.set()
            print("Connection to the TX-Controller has been lost!")
            self.parent.connection.close()


from .CommandCodes import x1Recv, x1Send
