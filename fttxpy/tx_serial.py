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

    # the internal X.1 data structure looks like this
    # all other data will be calculated as needed
    # TID/SID will be counted aumatically
    _exampleX1 = {
        "from": 2,
        "to": 1,
        "CC": 1,
        # "TA":
        #    {
        #        0: bytearray([0, 1, 2]),
        #        2: bytearray([3, 4, 5])
        #    },
        "TA": {},
        "ChecksumOK": True  # only present for recieved packages
    }

    def sendX1Package(self, data):
        # define package start and end
        PackageStart = bytearray([0x02, 0x55])
        PackageEnd = bytearray([0x03])
        # define package header len
        PackageHeaderLen = 20
        # check TAs present
        if len(data["TA"]):
            # assume every TA has same length
            # length of first TA multiplied by TA count is TA total length
            TALen = (
                len(data["TA"][list(data["TA"].keys())[0]]) + 4) * \
                len(data["TA"])
        else:
            # no TAs -> TA total length 0
            TALen = 0
        # calculate package length
        # (This is not the total length! This is just for the header field!)
        PackageLen = (PackageHeaderLen + TALen).to_bytes(2, byteorder='big')
        # calculate sender and reciever
        PackageFrom = data["from"].to_bytes(4, byteorder='little')
        PackageTo = data["to"].to_bytes(4, byteorder='little')
        PackageFromTo = PackageFrom + PackageTo
        # reset TID if it is near overflow
        # it seems that the TID is not needed...
        if self.X1TID > 65535:
            self.X1TID = 0
        # calculate TID and SID
        PackageTID = self.X1TID.to_bytes(2, byteorder='little')
        PackageSID = self.X1SID.to_bytes(2, byteorder='little')
        PackageTIDSID = PackageTID + PackageSID
        # calculate CommandCode
        PackageCC = data["CC"].to_bytes(4, byteorder='little')
        # calculate TA count
        PackageTAs = len(data["TA"]).to_bytes(4, byteorder='little')
        # combine package header fields
        PackageHeader = PackageStart + PackageLen + \
            PackageFromTo + PackageTIDSID + PackageCC + PackageTAs

        # prepare bytearray for package payload
        PackageData = bytearray([])
        # iterate over TAs
        for TANum, TAData in data["TA"].items():
            # calculate TA number
            TANumHex = TANum.to_bytes(4, byteorder='little')
            # append to data
            PackageData += TANumHex + TAData

        # combine header data with payload
        PackageHeaderData = PackageHeader + PackageData

        # prepare checksum variable
        checksum = 0
        # iterate over all bytes from package length to end of payload
        for b in PackageHeaderData[2:]:
            # substract byte from checksum variable
            checksum -= b
        # calculate checksum
        PackageChecksum = checksum.to_bytes(2, byteorder='big', signed=True)

        # combine package checksum and packahe end to package footer
        PackageFooter = PackageChecksum + PackageEnd
        # combine to full packge
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

        # tray to send package
        try:
            # send to serial connection
            self.ser.write(FULLPackage)
        except (serial.serialutil.SerialException,
                serial.serialutil.SerialTimeoutException):
            # return False in case of serial error
            return(False)
        # exit gracefully if unknown error
        # return True if ok
        return(True)

    def reciveX1Package(self):
        #wait for incoming data
        while self.ser.in_waiting == 0:
            pass
        #read data
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

        #prepare dict for package data
        Package = {}
        #get packge checksum
        PackageChecksum = int.from_bytes(serData[-3:-1], byteorder='big')
        #get data to calculate true checksum
        PackageChecksumArray = serData[2:-3]
        #prepare checksum variable
        PackageCalcChacksum = 65536
        # iterate over all bytes from package length to end of payload
        for b in PackageChecksumArray:
            # substract byte from checksum variable
            PackageCalcChacksum -= b
        #check whether checksums match
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
                    Package["TA"][int.from_bytes(
                        TAArray[:4], byteorder='little')] = TAArray[4:]
            return(True, Package)
        else:
            return(False, Package)

    def X1CMD(self, inData):
        self.SerialLock.acquire()
        for n in range(20):
            st = time.time()
            # count the Transaction ID 1 up
            self.X1TID += 1
            # send X.1 package and get status
            execOK = self.sendX1Package(inData)
            # kill if send error
            if not execOK:
                if Debug.PrintPackageSendError:
                    print("Package send error! Try", n + 1)
                continue
            # recieve X.1 package and get status and data
            execOK, retData = self.reciveX1Package()
            if not retData["ChecksumOK"]:
                if Debug.PrintChecksumError:
                    print("Checksum error! Try", n + 1)
                continue
            else:
                self.SerialLock.release()
                if Debug.PrintPackagePing:
                    print("Ping:", str((time.time() - st) * 1000), "mSek")
                # return ok status and data
                return(execOK, retData)
        self.SerialLock.release()
        return(False, {})
