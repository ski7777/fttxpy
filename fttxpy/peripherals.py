#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

from math import log


class motor():
    def __init__(self, parent, output):
        assert(type(output) == int and output in range(1, 5))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.output = output - 1
        self.outpins = [self.output * 2, self.output * 2 + 1]
        assert(not self.outer.getOutputLock(self.ext, self.outpins[0]))
        assert(not self.outer.getOutputLock(self.ext, self.outpins[1]))
        self.outer.setOutputLock(self.ext, self.outpins[0], True)
        self.outer.setOutputLock(self.ext, self.outpins[1], True)
        self.setSpeed(0)
        self.setDistance(0)

    def setSpeed(self, speed):
        assert(type(speed) == int and speed in range(-512, 513))
        if speed > 0:
            self.outer.setOutDuty(self.ext, self.outpins[0], speed)
            self.outer.setOutDuty(self.ext, self.outpins[1], 0)
        else:
            self.outer.setOutDuty(self.ext, self.outpins[0], 0)
            self.outer.setOutDuty(self.ext, self.outpins[1], -speed)

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
        self.setSpeed(0)
        self.setDistance(0)

    def __del__(self):
        self.outer.setOutputLock(self.ext, self.outpins[0], False)
        self.outer.setOutputLock(self.ext, self.outpins[1], False)


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


class output():
    def __init__(self, parent, output):
        assert(type(output) == int and output in range(1, 9))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.output = output - 1
        assert(not self.outer.getOutputLock(self.ext, self.output))
        self.outer.setOutputLock(self.ext, self.output, True)

    def setLevel(self, level):
        assert(type(level) == int and level in range(513))
        self.outer.setOutDuty(self.ext, self.output, level)

    def __del__(self):
        self.outer.setOutputLock(self.ext, self.output, False)


class resistor():
    def __init__(self, parent, input):
        assert(type(input) == int and input in range(1, 9))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.input = input - 1
        assert(not self.outer.getInputLock(self.ext, self.input))
        self.outer.setInputProfile(self.ext, self.input, ('R15K', False))
        self.outer.setInputLock(self.ext, self.input, True)

    def value(self):
        return(self.outer.getInputValue(self.ext, self.input))

    def ntcTemperature(self):
        r = self.value()
        if r != 0:
            x = log(self.value())
            y = x * x * 1.39323522
            z = x * -43.9417405
            T = y + z + 271.870481
        else:
            T = 10000
        return(T)

    def __del__(self):
        self.outer.setInputLock(self.ext, self.input, False)


class ultrasonic():
    def __init__(self, parent, input):
        assert(type(input) == int and input in range(1, 9))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.input = input - 1
        assert(not self.outer.getInputLock(self.ext, self.input))
        self.outer.setInputProfile(self.ext, self.input, ('US', False))
        self.outer.setInputLock(self.ext, self.input, True)

    def distance(self):
        return(self.outer.getInputValue(self.ext, self.input))

    def __del__(self):
        self.outer.setInputLock(self.ext, self.input, False)


class colorsensor():
    def __init__(self, parent, input):
        assert(type(input) == int and input in range(1, 9))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.input = input - 1
        assert(not self.outer.getInputLock(self.ext, self.input))
        self.outer.setInputProfile(self.ext, self.input, ('U10', False))
        self.outer.setInputLock(self.ext, self.input, True)

    def voltage(self):
        return(self.outer.getInputValue(self.ext, self.input))

    def color(self):
        c = self._outer.getCurrentInput(num - 1)
        if c < 200:
            return('weiss')
        elif c < 1000:
            return('rot')
        else:
            return('blau')

    def __del__(self):
        self.outer.setInputLock(self.ext, self.input, False)


class trailfollower():
    def __init__(self, parent, input):
        assert(type(input) == int and input in range(1, 9))
        self.parent = parent
        self.outer = self.parent.parent
        self.ext = self.parent.ext
        self.input = input - 1
        assert(not self.outer.getInputLock(self.ext, self.input))
        self.outer.setInputProfile(self.ext, self.input, ('U10', True))
        self.outer.setInputLock(self.ext, self.input, True)

    def state(self):
        return(self.outer.getInputValue(self.ext, self.input))

    def __del__(self):
        self.outer.setInputLock(self.ext, self.input, False)
