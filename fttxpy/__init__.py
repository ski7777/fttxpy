#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#


class Debug():
    PrintPackageRaw = False
    PrintUnknownPackageRaw = True
    PrintPackagePing = False
    PrintChecksumError = False
    PrintPackageSendError = False
    PrintPackageJSONRX = False
    PrintPackageJSONTX = False
    PrintSendRetriesWrongCC = False


# import TX functionalities
from .dev_helper import *
from .high_level import *
