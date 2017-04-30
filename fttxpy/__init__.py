#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# import TX functionalities
from .dev_helper import *
from .tx_serial import *

# get a list of TXs and connect to the first one
TXs = getTXDevices()
TX = TXSerial(TXs[0])
# test the communication
print(TX.getName())
print(TX.getVersion())
