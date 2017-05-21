#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import threading
from .tx_serial import *
from .CommandCodes import *


class ftTX():

    def __init__(self, dev):
        self.data_lock = threading.Lock()
        self.data = {}

        self.connection = TXSerial(dev)
        print(dev)

    def createTA(self, ta):
        new_ta = {}
        new_ta["io_config"] = {}
        new_ta["input_data"] = []
        for _ in range(8):
            new_ta["input_data"].append(0)
        new_ta["output_data"] = []
        for _ in range(8):
            new_ta["output_data"].append({})

        self.data_lock.acquire()
        self.data[ta] = new_ta
        self.data_lock.release()
