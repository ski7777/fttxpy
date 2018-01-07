#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import fnmatch
import pyudev

udevContext = pyudev.Context()


def getTXDevices(txc=True, ftduino=False):
    ACMList = []
    path = "/dev/"
    pattern = "ttyACM*"
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                ACMList.append(os.path.join(root, name))
    TXList = []
    for dev in ACMList:
        model = pyudev.Devices.from_device_file(udevContext, dev)["ID_MODEL"]
        if txc and model == "ROBO_TX_Controller" or ftduino and model == "ftDuino":
            TXList.append(dev)
    return(TXList)
