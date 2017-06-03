#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import serial
import time
import threading


class TXSerial():

    def __init__(self, dev):
        self.dev = dev
        # initialize the serial connection
        self.ser = serial.Serial(self.dev)
        self.SerialLock = threading.Lock()

        self.X1TID = 1  # will be counted up for each package sent by the PC
        self.X1SID = 0  # will start at 0 and then set by TX-C

    def close(self):
        self.SerialLock.acquire()
        self.ser.close()
        self.SerialLock.release()

    def reOpen(self):
        self.SerialLock.acquire()
        self.ser.open()
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
        "CRCok": True  # only present for recieved packages
    }

    def sendX1Package(self, data):
        """
        """
        PackageStart = bytearray([0x02, 0x55])
        PackageEnd = bytearray([0x03])
        PackageHeaderLen = 20
        try:
            TALen = len(data["TA"][list(data["TA"].keys())[0]]) * len(data["TA"])
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
        PackageHeader = PackageLen + PackageFromTo + PackageTIDSID + PackageCC + PackageTAs

        PackageData = bytearray([])
        PackageHeaderData = PackageHeader + PackageData

        Chacksum = 0
        for b in PackageHeaderData:
            Chacksum -= b
        PackageChecksum = Chacksum.to_bytes(2, byteorder='big', signed=True)
        PackageFooter = PackageChecksum + PackageEnd

        PackageHeaderData = PackageHeaderData + PackageStart
        FULLPackage = PackageHeaderData + PackageFooter

        i = 0
        while True:
            exit = False
            array = []
            for x in range(4):
                try:
                    array.append(FULLPackage[i + x])
                except:
                    exit = True
            print(str(i) + ":" + " ".join("%02x" % b for b in array))
            i += 4
            if exit:
                break

        return(True)

    def reciveX1Package(self):
        """
        """
        return(True, {})

    def X1CMD(slef, inData):
        """
        send a X.1 package and return data
        """
        self.SerialLock.acquire()
        # count the Transaction ID 1 up
        self.X1TID += 1
        # send X.1 package and get status
        ok = self.sendX1Package(inData)
        # kill if send error
        if not ok:
            self.SerialLock.release()
            return(False, {})
        # recieve X.1 package and get status and data
        ok, retData = self.reciveX1Package()
        self.SerialLock.release()
        # kill if recieve error
        if not ok:
            return(False, {})
        # return ok status and data
        return(True, {})
