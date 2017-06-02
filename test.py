#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from fttxpy import *
import time

# get a list of TXs and connect to the first one
TXs = getTXDevices()
print("Found " + str(len(TXs)) + " TX Controller")
print(TXs)

TX = fttxpy()
programs = TX.getPrograms()
TX.execProgramö(programs[0])
time.sleep(1)
TX.stopProgram()
