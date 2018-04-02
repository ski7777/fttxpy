#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from .low_level import *
from .dev_helper import *
from .peripherals import *
import os.path


class fttxpy(ftTX):

    def __init__(self, dev="", txc=True, ftduino=False):
        if dev == "":
            TXs = getTXDevices(txc, ftduino)
            if len(TXs) == 0:
                print("No TX-Controllers found!")
                raise FileNotFoundError
            else:
                print("Found", str(len(TXs)), "TX-Controller(s). Automatically selecting the first one!")
                dev = TXs[0]
        if not os.path.exists(dev):
            print("Could not find specified TX-Controller!")
            raise FileNotFoundError
        ftTX.__init__(self, dev)
        print("Connected to", self.getName(), "Version", self.getVersion())
        self.extensionInfo()

    def extensionInfo(self):
        extList = list(self.Data.keys())
        extList.remove(0)
        extStrList = []
        if len(extList) > 0:
            for ext in extList:
                extStrList.append("Ext " + str(ext) + " (" + self.getName(ext) + ", " + self.getVersion(ext) + ")")
            print("Found extensions:", ", ".join(extStrList))

    def robotx(self, ext=0):
        assert(type(ext) == int and ext in self.Data)
        return(robotx(self, ext))


class robotx():
    def __init__(self, parent, ext):
        self.parent = parent
        self.ext = ext

    def getName(self):
        return(self.parent.getName(self.ext))

    def getVersion(self):
        return(self.parent.getVersion(self.ext))

    def motor(self, o):
        return(motor(self, o))

    def input(self, i):
        return(TXinput(self, i))

    def output(self, o):
        return(output(self, o))

    def resistor(self, i):
        return(resistor(self, i))

    def ultrasonic(self, i):
        return(ultrasonic(self, i))

    def colorsensor(self, i):
        return(colorsensor(self, i))

    def trailfollower(self, i):
        return(trailfollower(self, i))
