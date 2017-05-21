#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from .low_level import *


class fttxpy(ftTX):

    def __init__(self, dev):
        ftTX.__init__(self, dev)
