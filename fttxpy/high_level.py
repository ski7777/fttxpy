#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from .low_level import *
from .dev_helper import *
import os.path


class fttxpy(ftTX):

    def __init__(self, dev=""):
        if dev == "":
            TXs = getTXDevices()
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

    def execProgram(self, name):
        self.loadProgram(name)
        self.runProgram()
