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

    def execProgram(self, name):
        self.loadProgram(name)
        self.runProgram()
