#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from fttxpy import *
import time

# get a list of TXs and connect to the first one
TXs = getTXDevices()
print("Found " + str(len(TXs)) + " TX Controller")
print(TXs)
if len(TXs) > 0:
    print("----------")
    for TX in TXs:
        con = TXSerial(TX)
        print(TX, con.getName(), con.getVersion())
        programs = con.getPrograms()
        if len(programs) > 0:
            program_str = ""
            for prog in programs:
                if program_str == "":
                    program_str = prog
                else:
                    program_str = program_str + ", " + prog
            print("  -Found " + str(len(programs)) + " programs: " + program_str)
        else:
            print("  -Found no programs!")
        con.close()
    print("----------")
    # select the first TX-C for some tests
    #TX = TXSerial(TXs[0])
    # test the communication
    #programs = TX.getPrograms()
    #TX.loadProgram(programs[0])
    #TX.runProgram()
    #time.sleep(1)
    #TX.stopProgram()
