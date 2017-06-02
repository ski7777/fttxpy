#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import fnmatch
import pyudev

udevContext = pyudev.Context()


def getTXDevices():
    ACMList = []
    path = "/dev/"
    pattern = "ttyACM*"
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                ACMList.append(os.path.join(root, name))
    TXList = []
    for dev in ACMList:
        if pyudev.Devices.from_device_file(udevContext, dev)["ID_MODEL"] == "ROBO_TX_Controller":
            TXList.append(dev)
    return(TXList)
