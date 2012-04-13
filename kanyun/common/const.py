#!/usr/bin/env python
# encoding: utf-8
# TAB char: space[4]
#
# Last update: Yuwei Peng<pengyuwei@gmail.com> 2012-4-6
#
# Copyright 2012 Sina Corporation
# All Rights Reserved.
# Author: YuWei Peng <pengyuwei@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging


class MSG_TYPE:
    HEART_BEAT = '0'
    LOCAL_INFO = '1'
    TRAFFIC_ACCOUNTING = '2'
    AGENT = '3'
    
class STATISTIC:
    SUM     = 0
    MAXIMUM = 1
    MINIMUM = 2
    AVERAGE = 3
    SAMPLES = 4

statistic_str = dict()
statistic_str[STATISTIC.SUM] = "SUM"
statistic_str[STATISTIC.MAXIMUM] = "MAXIMUM"
statistic_str[STATISTIC.MINIMUM] = "MINIMUM"
statistic_str[STATISTIC.AVERAGE] = "AVERAGE"
statistic_str[STATISTIC.SAMPLES] = "SAMPLES"

