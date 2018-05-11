#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

# fttxpy X.1 Command Codes
# import the low level class to process the return data
from .low_level import ftTX

# create two dummy classes


def CCNoProcessing(self, data):
    return(True)


x1Recv = {
    101: CCNoProcessing,  # EchoReply
    102: ftTX.X1IOReply,  # InputReply
    105: CCNoProcessing,  # ConfigWReply
    106: ftTX.X1InfoReply,  # InfoReply
    107: ftTX.X1StateReply  # StateReply
}

x1Send = {
    "echo": 1,
    "IO": 2,
    "configW": 5,
    "info": 6,
    "state": 7
}
