#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import serial
import time
import threading
from . import Debug


class TXSerial():

    def __init__(self, dev):
        self.dev = dev
        # initialize the serial connection
        self.ser = serial.Serial(self.dev)
        self.ser.read_all()
        self.SerialLock = threading.Lock()

        self.X1TID = 0  # will be counted up for each package sent by the PC
        self.X1SID = 0  # will start at 0 and then set by TX-C

    def close(self):
        self.SerialLock.acquire()
        self.ser.close()
        self.SerialLock.release()

    def reOpen(self):
        self.SerialLock.acquire()
        self.ser.open()
        self.ser.read_all()
        self.SerialLock.release()

    def readToList(self):
        """
        Read all serial data to a list
        """
        # wait a moment for the data and read
        time.sleep(0.05)
        read = self.ser.read_all()
        # convert data to lines and add it to a list
        rawData = read.splitlines()
        data = []
        for line in rawData:
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
        self.SerialLock.acquire()
        # send data with carriage return and get data
        self.ser.write((cmd + "\r").encode())
        serData = self.readToList()
        self.SerialLock.release()
        # remove the command itself
        serData.pop(0)
        return(serData)

    # the internal X.1 data structure looks like this
    # all other data will be calculated as needed / TID/SID will be counted aumatically
    _exampleX1 = {
        "from": 2,
        "to": 1,
        "CC": 1,
        #"TA":
        #    {
        #        0: bytearray([0, 1, 2]),
        #        2: bytearray([3, 4, 5])
        #    },
        "TA": {},
        "ChecksumOK": True  # only present for recieved packages
    }

    def sendX1Package(self, data):
        """
        """
        PackageStart = bytearray([0x02, 0x55])
        PackageEnd = bytearray([0x03])
        PackageHeaderLen = 20
        try:
            TALen = (len(data["TA"][list(data["TA"].keys())[0]]) + 4) * len(data["TA"])
        except IndexError:
            TALen = 0
        PackageLen = (PackageHeaderLen + TALen).to_bytes(2, byteorder='big')
        PackageFrom = data["from"].to_bytes(4, byteorder='little')
        PackageTo = data["to"].to_bytes(4, byteorder='little')
        PackageFromTo = PackageFrom + PackageTo
        PackageTID = self.X1TID.to_bytes(2, byteorder='little')
        PackageSID = self.X1SID.to_bytes(2, byteorder='little')
        PackageTIDSID = PackageTID + PackageSID
        PackageCC = data["CC"].to_bytes(4, byteorder='little')
        PackageTAs = len(data["TA"]).to_bytes(4, byteorder='little')
        PackageHeader = PackageStart + PackageLen + PackageFromTo + PackageTIDSID + PackageCC + PackageTAs

        PackageData = bytearray([])
        for TANum, TAData in data["TA"].items():
            TANumHex = TANum.to_bytes(4, byteorder='little')
            PackageData = PackageData + TANumHex + TAData

        PackageHeaderData = PackageHeader + PackageData

        Chacksum = 0
        for b in PackageHeaderData[2:]:
            Chacksum -= b
        PackageChecksum = Chacksum.to_bytes(2, byteorder='big', signed=True)

        PackageFooter = PackageChecksum + PackageEnd
        FULLPackage = PackageHeaderData + PackageFooter

        if Debug.PrintPackageRaw:
            print("\nSending:")
            i = 0
            while True:
                exit = False
                array = []
                for x in range(4):
                    try:
                        array.append(FULLPackage[i + x])
                    except IndexError:
                        exit = True
                print(str(i) + ":" + " ".join("%02x" % b for b in array))
                i += 4
                if exit:
                    break
        try:
            self.ser.write(FULLPackage)
        except (serial.serialutil.SerialException, serial.serialutil.SerialTimeoutException):
            return(False)
        return(True)

    def reciveX1Package(self):
        """
        """
        while self.ser.in_waiting == 0:
            pass
        serData = self.ser.read_all()

        i = 0
        if Debug.PrintPackageRaw:
            print("\nRecieving:")
            while True:
                exit = False
                array = []
                for x in range(4):
                    try:
                        array.append(serData[i + x])
                    except IndexError:
                        exit = True
                print(str(i) + ":" + " ".join("%02x" % b for b in array))
                i += 4
                if exit:
                    break

        Package = {}
        #Package["raw"] = serData
        PackageChecksum = int.from_bytes(serData[-3:-1], byteorder='big')
        PackageChecksumArray = serData[2:-3]
        PackageCalcChacksum = 65536
        for b in PackageChecksumArray:
            PackageCalcChacksum -= b
        ChecksumOK = PackageCalcChacksum == PackageChecksum
        Package["ChecksumOK"] = ChecksumOK
        if ChecksumOK:
            PackageLen = int.from_bytes(serData[2:4], byteorder='big')
            Package["from"] = int.from_bytes(serData[4:8], byteorder='little')
            Package["to"] = int.from_bytes(serData[8:12], byteorder='little')
            Package["CC"] = int.from_bytes(serData[16:20], byteorder='little')
            TAs = int.from_bytes(serData[20:24], byteorder='little')
            self.X1SID = int.from_bytes(serData[14:16], byteorder='little')
            Package["TA"] = {}
            PackageTALen = PackageLen - 20
            if TAs:
                SingleTALen = int(PackageTALen / TAs)
                if PackageTALen % TAs != 0:
                    return(False, Package)
                for TAIndex in range(TAs):
                    TAArrayStart = 24 + (SingleTALen * TAIndex)
                    TAArrayStop = 24 + (SingleTALen * (TAIndex + 1))
                    TAArray = serData[TAArrayStart:TAArrayStop]
                    Package["TA"][int.from_bytes(TAArray[:4], byteorder='little')] = TAArray[4:]
            return(True, Package)
        else:
            return(False, Package)

    def X1CMD(self, inData):
        """
        send a X.1 package and return data
        """
        st = time.time()
        self.SerialLock.acquire()
        # count the Transaction ID 1 up
        self.X1TID += 1
        # send X.1 package and get status
        execOK = self.sendX1Package(inData)
        # kill if send error
        if not execOK:
            self.SerialLock.release()
            return(False, {})
        # recieve X.1 package and get status and data
        execOK, retData = self.reciveX1Package()
        self.SerialLock.release()
        if Debug.PrintPackagePing:
            print("Ping:", str((time.time() - st) * 1000), "mSek")
        # return ok status and data
        return(execOK, retData)
