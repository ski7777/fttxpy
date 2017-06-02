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
        self.serial_lock = threading.Lock()

        self.X1_TID = 0  # will be counted up for each package sent by the PC
        self.X1_SID = 0  # will start at 0 and then set by TX-C

    def close(self):
        self.serial_lock.acquire()
        self.ser.close()
        self.serial_lock.release()

    def reOpen(self):
        self.serial_lock.acquire()
        self.ser.open()
        self.serial_lock.release()

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
        self.serial_lock.acquire()
        # send data with carriage return and get data
        self.ser.write((cmd + "\r").encode())
        ser_data = self.readToList()
        self.serial_lock.release()
        # remove the command itself
        ser_data.pop(0)
        return(ser_data)

    # the internal X.1 data structure looks like this
    # all other data will be calculated as needed / TID/SID will be counted aumatically
    __exampleX1 = {
        "from": 0,
        "to": 0,
        "CC": 0,
        "TA":
            {
                0: "bytes",
                2: "bytes"
            },
        "CRC_ok": True  # only present for recieved packages
    }

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
        self.serial_lock.acquire()
        # count the Transaction ID 1 up
        self.X1TID += 1
        # send X.1 package and get status
        ok = self.sendX1Package(in_data)
        # kill if send error
        if not ok:
            self.serial_lock.release()
            return(False, {})
        # recieve X.1 package and get status and data
        ok, ret_data = self.reciveX1Package()
        self.serial_lock.release()
        # kill if recieve error
        if not ok:
            return(False, {})
        # return ok status and data
        return(True, {})
