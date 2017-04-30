#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import fnmatch
import pyudev

udev_context = pyudev.Context()


def getTXDevices():
    ACM_list = []
    path = "/dev/"
    pattern = "ttyACM*"
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                ACM_list.append(os.path.join(root, name))
    TX_list = []
    for dev in ACM_list:
        if pyudev.Devices.from_device_file(udev_context, dev)["ID_MODEL"] == "ROBO_TX_Controller":
            TX_list.append(dev)
    return(TX_list)
