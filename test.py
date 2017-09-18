#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import time

from fttxpy import *

TX = fttxpy()
TX.Data[0]["Output"]["Distance"][0] = 500
TX.Data[0]["Output"]["ID"][0] += 1
TX.Data[0]["Output"]["Duty"][0] = 512
TX.waitOnDataExchange()
print("Sent")
while True:
    if TX.Data[0]["Output"]["PosReached"][0]:
        print("OK")
        break
#print(json.dumps(TX.Data, indent=4, sort_keys=True))
