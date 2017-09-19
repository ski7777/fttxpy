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

    def robotx(self, ext=0):
        assert(type(ext) == int and ext in self.Data)

        class robotx():
            def __init__(self, parent, ext):
                self.parent = parent
                self.ext = ext

            def getName(self):
                return(self.parent.getName(self.ext))

            def getVersion(self):
                return(self.parent.getVersion(self.ext))

            def motor(self, output):
                class motor():
                    def __init__(self, parent, output):
                        assert(type(output) == int and output in range(1, 5))
                        self.parent = parent
                        self.outer = self.parent.parent
                        self.ext = self.parent.ext
                        self.output = output - 1
                        self.setSpeed(0)
                        self.setDistance(0)

                    def setSpeed(self, speed):
                        assert(type(speed) == int and speed in range(-512, 513))
                        if speed > 0:
                            self.outer.setOutDuty(self.ext, self.output * 2, speed)
                            self.outer.setOutDuty(self.ext, self.output * 2 + 1, 0)
                        else:
                            self.outer.setOutDuty(self.ext, self.output * 2, 0)
                            self.outer.setOutDuty(self.ext, self.output * 2 + 1, -speed)

                    def setDistance(self, distance, syncto=None):
                        assert(type(distance) == int)
                        if syncto:
                            self.outer.setMotSync(self.ext, self.output, syncto.output + 1)
                            self.outer.setMotSync(self.ext, syncto.output, self.output + 1)
                            self.outer.setMotDistance(self.ext, self.output, distance)
                            self.outer.setMotDistance(self.ext, syncto.output, distance)
                            self.outer.incrMotID(self.ext, self.output)
                            self.outer.incrMotID(self.ext, syncto.output)
                        else:
                            self.outer.setMotSync(self.ext, self.output, 0)
                            self.outer.setMotDistance(self.ext, self.output, distance)
                            self.outer.incrMotID(self.ext, self.output)

                    def finished(self):
                        return(self.outer.getMotIsFinished(self.ext, self.output))

                    def getCurrentDistance(self):
                        return(self.outer.getCounterValue(self.ext, self.output))

                    def stop(self):
                        pass
                return(motor(self, output))

        return(robotx(self, ext))
