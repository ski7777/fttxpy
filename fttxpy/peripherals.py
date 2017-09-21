#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#


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


class TXinput():  # renamed due conflict with built-in input()
    def __init__(self, parent, input):
        assert(type(input) == int and input in range(1, 9))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.input = input - 1
        assert(not self.outer.getInputLock(self.ext, self.input))
        self.outer.setInputProfile(self.ext, self.input, ('R5K', True))
        self.outer.setInputLock(self.ext, self.input, True)

    def state(self):
        return(self.outer.getInputValue(self.ext, self.input))

    def __del__(self):
        self.outer.setInputLock(self.ext, self.input, False)
