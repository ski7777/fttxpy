#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from fttxpy import *
TX = fttxpy()
print("-----")
Pack = {
    "from": 2,
    "to": 1,
    "CC": 1,
    "TA": {},
}

print("Sending CC:", str(Pack["CC"]))
x = TX.connection.X1CMD(Pack)#, printPackage=True)
print(x[0])
print(x[1])


print("-----")
Pack = {
    "from": 2,
    "to": 1,
    "CC": 6,
    "TA": {0: bytearray([])},
}

print("Sending CC:", str(Pack["CC"]))
x = TX.connection.X1CMD(Pack)  # , printPackage=True)
print(x[0])
print(x[1])
