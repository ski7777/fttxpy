#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import time

from fttxpy import *

TX = fttxpy()
master = TX.robotx()
ext1 = TX.robotx(1)
mot1 = master.motor(1)
mot2 = master.motor(2)
mot1.setDistance(1000, mot2)
mot1.setSpeed(512)
mot2.setSpeed(512)
for _ in range(5):
    TX.waitOnDataExchange()
while not (mot1.finished() and mot2.finished()):
    print(mot1.getCurrentDistance(), mot2.getCurrentDistance())
    time.sleep(0.1)
input()
#print(json.dumps(TX.Data, indent=4, sort_keys=True))
