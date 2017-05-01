#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from fttxpy import *
import time
# get a list of TXs and connect to the first one
TXs = getTXDevices()
print("Found " + str(len(TXs)) + " TX Controller")
if len(TXs) > 0:
    print("----------")
    for TX in TXs:
        con = TXSerial(TX)
        print(con.getName(), con.getVersion())
        con.close()
    print("----------")
    # select the first TX-C for some tests
    TX = TXSerial(TXs[0])
    # test the communication
    programs = TX.getPrograms()
    print(programs)
    TX.loadProgram(programs[0])
    TX.runProgram()
    time.sleep(1)
    TX.stopProgram()
