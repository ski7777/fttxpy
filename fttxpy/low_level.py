#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import threading
import time
from .tx_serial import *
from . import Debug

C_INPUT_MODE_U = 0
C_INPUT_MODE_R = 1
C_INPUT_MODE_R2 = 2
C_INPUT_MODE_US = 3
InputModes = {
    "U10": C_INPUT_MODE_U,
    "R5K": C_INPUT_MODE_R,
    "R15K": C_INPUT_MODE_R2,
    "US": C_INPUT_MODE_US
}

maxRetriesAfterUnknownCC = 3


class ftTX():

    def __init__(self, dev):
        self.DataLock = threading.Lock()
        self.ConfigChanged = threading.Event()
        self.exchangeDataEvent = threading.Event()
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
            raise ConnectionAbortedError
        self.Thread = self.KeepConnectionThread(self)
        self.Thread.setDaemon(True)
        self.Thread.start()

    def createTA(self, ta):
        newTA = {}
        newTA["Input"] = {}
        newTA["Input"]["Digital"] = []
        for _ in range(8):
            newTA["Input"]["Digital"].append(True)
        newTA["Input"]["Value"] = []
        for _ in range(8):
            newTA["Input"]["Value"].append(0)
        newTA["Input"]["Mode"] = []
        for _ in range(8):
            newTA["Input"]["Mode"].append(C_INPUT_MODE_R)
        newTA["Input"]["Lock"] = []
        for _ in range(8):
            newTA["Input"]["Lock"].append(False)

        newTA["Counter"] = {}
        newTA["Counter"]["Reset"] = []
        for _ in range(4):
            newTA["Counter"]["Reset"].append(False)
        newTA["Counter"]["ID"] = []
        for _ in range(4):
            newTA["Counter"]["ID"].append(0)
        newTA["Counter"]["Executed"] = []
        for _ in range(4):
            newTA["Counter"]["Executed"].append(0)
        newTA["Counter"]["Count"] = []
        for _ in range(4):
            newTA["Counter"]["Count"].append(0)
        newTA["Counter"]["State"] = []
        for _ in range(4):
            newTA["Counter"]["State"].append(False)

        newTA["Output"] = {}
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
        newTA["Output"]["PosReached"] = []
        for _ in range(4):
            newTA["Output"]["PosReached"].append(True)
        newTA["Output"]["Lock"] = []
        for _ in range(8):
            newTA["Output"]["Lock"].append(False)

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
        self.DataLock.acquire()
        try:
            assert(type(TXn) == int and TXn in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        data = self.Data[TXn]["meta"]["name"]
        self.DataLock.release()
        return(data)

    def getVersion(self, TXn=0):
        """
        get TX-C Firmware version
        """
        self.DataLock.acquire()
        try:
            assert(type(TXn) == int and TXn in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        data = self.Data[TXn]["meta"]["ver"]
        self.DataLock.release()
        return(data)

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
        if Debug.PrintPackageJSONTX:
            print("TX:", data)
        retry = 0
        OK = False
        while retry < maxRetriesAfterUnknownCC and not OK:
            if retry > 0 and Debug.PrintSendRetriesWrongCC:
                print("Wrong CC! Retry:", retry)
            execOK, retData = self.connection.X1CMD(data)
            if Debug.PrintPackageJSONRX:
                print("RX:", retData)
            if not execOK:
                return(False)
            retry += 1
            if retData["CC"] in x1Recv:
                OK = True
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
        self.ConfigChanged.clear()
        execOK = self.X1ConfigWSend()
        if not execOK:
            return(False)
        return(True)

    def X1CreateFillData(self, length, fill=0):
        data = bytearray()
        for _ in range(length):
            data.append(fill)
        return(data)

    def X1EchoSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["echo"]
        execOK = self.executeX1(data)
        return(execOK)

    def X1InfoSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["info"]
        self.DataLock.acquire()
        for n in self.Data.keys():
            data["TA"][n] = bytearray()
        self.DataLock.release()
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
                    TXd["Counter"]["ID"][n] += 1
                    TXd["Counter"]["Reset"][n] = False
                CounterResetData = CounterResetData + TXd["Counter"]["ID"][n].to_bytes(2, byteorder='little')
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
                self.Data[TAn]["Counter"]["Executed"][n] = int.from_bytes(TAd[32 + (2 * n):32 + (2 * n) + 2], byteorder='little', signed=False) == self.Data[TAn]["Counter"]["ID"][n]
            for n in range(4):
                self.Data[TAn]["Output"]["PosReached"][n] = int.from_bytes(TAd[40 + (2 * n):40 + (2 * n) + 2], byteorder='little', signed=False) == self.Data[TAn]["Output"]["ID"][n]
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

    def X1ConfigWSend(self):
        data = self.DefaultPackage.copy()
        data["CC"] = x1Send["configW"]
        self.DataLock.acquire()
        for TXn, TXd in self.Data.items():
            InputData = bytearray()
            for n in range(8):
                InputData.append(TXd["Input"]["Digital"][n] * 128 + TXd["Input"]["Mode"][n])
            data["TA"][TXn] = self.X1CreateFillData(4, 1) + InputData + self.X1CreateFillData(4, 1) + self.X1CreateFillData(32)
        self.DataLock.release()
        execOK = self.executeX1(data)
        if not execOK:
            return(False)
        return(True)

    def waitOnDataExchange(self):
        while not self.exchangeDataEvent.isSet():
            pass
        self.exchangeDataEvent.wait()

    def incrMotID(self, ext, mot):
        assert(type(mot) == int and mot in range(4))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Output"]["ID"][mot] += 1
        self.DataLock.release()

    def setOutDuty(self, ext, out, duty):
        assert(type(out) == int and out in range(8))
        assert(type(duty) == int and duty in range(-512, 513))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Output"]["Duty"][out] = duty
        self.DataLock.release()

    def setMotSync(self, ext, master, slave):
        assert(type(master) == int and master in range(4))
        assert(type(slave) == int and slave in range(5))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Output"]["Sync"][master] = slave
        self.DataLock.release()

    def setMotDistance(self, ext, mot, distance):
        assert(type(mot) == int and mot in range(4))
        assert(type(distance) == int)
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Output"]["Distance"][mot] = distance
        self.DataLock.release()

    def getMotIsFinished(self, ext, mot):
        assert(type(mot) == int and mot in range(4))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        finished = self.Data[ext]["Output"]["PosReached"][mot]
        self.DataLock.release()
        return(finished)

    def getCounterValue(self, ext, cnt):
        assert(type(cnt) == int and cnt in range(4))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        value = self.Data[ext]["Counter"]["Count"][cnt]
        self.DataLock.release()
        return(value)

    def getInputLock(self, ext, inp):
        assert(type(inp) == int and inp in range(8))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        value = self.Data[ext]["Input"]["Lock"][inp]
        self.DataLock.release()
        return(value)

    def setInputLock(self, ext, inp, state):
        assert(type(inp) == int and inp in range(8))
        assert(type(state) == bool)
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Input"]["Lock"][inp] = state
        self.DataLock.release()

    def getOutputLock(self, ext, out):
        assert(type(out) == int and out in range(8))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        value = self.Data[ext]["Output"]["Lock"][out]
        self.DataLock.release()
        return(value)

    def setOutputLock(self, ext, out, state):
        assert(type(out) == int and out in range(8))
        assert(type(state) == bool)
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Output"]["Lock"][out] = state
        self.DataLock.release()

    def setInputProfile(self, ext, inp, profile):
        assert(type(inp) == int and inp in range(8))
        assert(profile[0] in InputModes)
        assert(type(profile[1]) == bool)
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        self.Data[ext]["Input"]["Digital"][inp] = profile[1]
        self.Data[ext]["Input"]["Mode"][inp] = InputModes[profile[0]]
        self.DataLock.release()
        self.waitOnDataExchange()
        self.ConfigChanged.set()

    def getInputValue(self, ext, inp):
        assert(type(inp) == int and inp in range(8))
        self.DataLock.acquire()
        try:
            assert(type(ext) == int and ext in self.Data)
        except AssertionError:
            self.DataLock.release()
            raise AssertionError
        value = self.Data[ext]["Input"]["Value"][inp]
        self.DataLock.release()
        return(value)

    class KeepConnectionThread(threading.Thread):

        def __init__(self, parent):
            threading.Thread.__init__(self)
            self.parent = parent
            self.stopEvent = threading.Event()
            self.parent.ConfigChanged.set()

        def run(self):
            while not self.stopEvent.isSet():
                start = time.time()
                # Every failing serial Communication will trigger:
                # self.stopThread()
                if self.parent.ConfigChanged.isSet():
                    runOK = self.parent.exchangeConfig()
                    if not runOK:
                        self.stopThread()
                        break
                runOK = self.parent.exchangeData()
                if not runOK:
                    self.stopThread()
                    break
                self.parent.exchangeDataEvent.set()
                while time.time() - self.parent.exchangeInterval < start:
                    time.sleep(0.005)
                self.parent.exchangeDataEvent.clear()

        def stopThread(self):
            self.stopEvent.set()
            print("Connection to the TX-Controller has been lost!")
            self.parent.connection.close()
            raise BrokenPipeError


from .CommandCodes import x1Recv, x1Send
