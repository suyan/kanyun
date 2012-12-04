# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

import unittest
import time
import sys
import random
import mox
import pycassa
#from collections import OrderedDict
try:
   from collections import OrderedDict
except ImportError:
   from ordereddict import OrderedDict


from kanyun.server.data_server import *
from kanyun.common.app import *

class DbMox():
    def __init__(self):
        pass
    def insert(self, a=None,b=None,c=None,d=None,e=None):
        pass

class TestLivingStatus(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()
        
    def tearDown(self):
        self.mox.UnsetStubs()
    
    def testLivingStatusFunc(self):
        time.clock()
        ls = LivingStatus()
        print 'living'
        ls.update()
        self.assertTrue(not ls.is_die())
        ls.dietv = 5
        while not ls.is_die():
            now = time.localtime()
            sys.stdout.write("\r%02d:%02d:%02d waitting for die" % 
                                (now.tm_hour, now.tm_min, now.tm_sec))
            sys.stdout.flush()
            time.sleep(1)
        print
        ret = ls.on_die()
        print 'first event:', ret
        self.assertTrue(ret == 2)
        
        ret = ls.on_die()
        print 'next event:', ret
        self.assertTrue(ret == 0)
        print "LivingStatus test \t[\033[1;33mOK\033[0m]"
    
    
class TestDataServer(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()
        
    def tearDown(self):
        self.mox.UnsetStubs()
    
    def testDataServerFunc(self):
        time.clock()
        db = None
        data = None
        app = App(conf="kanyun.conf")
        autotask_heartbeat()
        clean_die_warning()
        list_workers()
        plugin_heartbeat(app, db, data)
        plugin_decoder_agent(app, db, data)
        plugin_decoder_traffic_accounting(app, db, data)
        print "DataServerFunc test \t[\033[1;33mOK\033[0m]"
        
    def testPluginDecoderTrafficAccounting(self):
        app = App(conf="kanyun.conf")
        data = {'240@venus-133': ('10.0.0.2', 1332409327, '0')}
        db = DbMox()
        plugin_decoder_traffic_accounting(app, db, data)


if __name__ == '__main__':
    time.clock()
    ApiTestSuite = unittest.TestSuite()
    ApiTestSuite.addTest(TestLivingStatus("testLivingStatusFunc"))
    ApiTestSuite.addTest(TestDataServer("testPluginDecoderTrafficAccounting"))
    ApiTestSuite.addTest(TestDataServer("testDataServerFunc"))

    
    runner = unittest.TextTestRunner()
    runner.run(ApiTestSuite)
