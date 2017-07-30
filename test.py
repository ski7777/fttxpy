#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from fttxpy import *
import json
TX = fttxpy()
print("-----")
input()
TX.Data[0]["Output"]["Duty"][0] = 512
input()
print("-----END-----")
print(json.dumps(TX.Data, indent=4, sort_keys=True))
