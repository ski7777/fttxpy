#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import time

from fttxpy import *

TX = fttxpy()
while True:
    TX.Data[0]["Output"]["Duty"][1] = 0
    TX.Data[1]["Output"]["Duty"][1] = 0
    for x in range(1, 513):
        TX.Data[0]["Output"]["Duty"][0] = x
        TX.Data[1]["Output"]["Duty"][0] = x
        time.sleep(0.005 + 0.005 / 512 * x)
    time.sleep(0.2)
    for x in reversed(range(0, 512)):
        TX.Data[0]["Output"]["Duty"][0] = x
        TX.Data[1]["Output"]["Duty"][0] = x
        time.sleep(0.005 + 0.005 / 512 * x)
    TX.Data[0]["Output"]["Duty"][0] = 0
    TX.Data[1]["Output"]["Duty"][0] = 0
    for x in range(1, 513):
        TX.Data[0]["Output"]["Duty"][1] = x
        TX.Data[1]["Output"]["Duty"][1] = x
        time.sleep(0.005 + 0.005 / 512 * x)
    time.sleep(0.2)
    for x in reversed(range(0, 512)):
        TX.Data[0]["Output"]["Duty"][1] = x
        TX.Data[1]["Output"]["Duty"][1] = x
        time.sleep(0.005 + 0.005 / 512 * x)
#print(json.dumps(TX.Data, indent=4, sort_keys=True))
