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

import time
import signal

from nova.notifier import api as notifier

import plugin_agent_srv
from kanyun.common.const import *
from kanyun.common.app import *
from kanyun.common.nova_tools import *

"""
Save the vm's system info data to db.
protocol:
    http://wiki.sinaapp.com/doku.php?id=monitoring
"""
living_status = dict()

app = App(conf="kanyun.conf", name="server")
logger = app.get_logger()
#tool = None
tool = NovaTools(app)


class LivingStatus():

    def __init__(self, worker_id='1'):
        self.dietv = 2 * 60  # default die threshold value: 2min
        self.alert_interval = 60  # one alert every 60 seconds
        self.update()
        self.alerted = False
        self.worker_id = worker_id
        self.previous_alert_time = 0

    def update(self):
        self.update_time = time.time()
        self.alerted = False

    def is_die(self):
        return time.time() - self.update_time > self.dietv

    def on_die(self):
        ret = 0
        if not self.alerted:
            ret += 1
            self.alert_once()

        # each minutes less than once
        if time.time() - self.previous_alert_time > self.alert_interval:
            self.alert()
            ret += 1

        return ret

    ####### private ########
    def alert_once(self):
        # TODO: dispose timeout worker here
        print '*' * 400
        print '[WARNING]worker', self.worker_id, "is dead. email sendto admin"
        print '*' * 400
        payload = dict()
        payload['host'] = FLAGS.my_ip
        payload['message'] = 'kanyun-worker is dead'
        notifier.notify(notifier.publisher_id('compute'), 'kanyun.worker', notifier.WARN, payload)
        self.alerted = True

    def alert(self):
        print '\033[0;31m[WARNING]\033[0mworker', self.worker_id, "is dead. Total=", len(living_status)
        self.previous_alert_time = time.time()


def autotask_heartbeat():
    global living_status
    for worker_id, ls in living_status.iteritems():
        if ls.is_die():
            try:
                ls.on_die()
            except Exception, e:
                print e


def clean_die_warning():
    global config
    global living_status

    new_list = dict()
    i = 0
    for worker_id, ls in living_status.iteritems():
        if not ls.is_die():
            new_list[worker_id] = ls
        else:
            i = i + 1

    living_status = new_list
    print i, "workers cleaned:"


def list_workers():
    global living_status
    print "-" * 30, "list_workers", "-" * 30
    for worker_id, ls in living_status.iteritems():
        print 'worker', worker_id, "update @", ls.update_time
    print len(living_status), "workers."


def get_prefix(data, s='@'):
    try:
        prefix = data.split(s)[0]
        return prefix
    except Exception, e:
        print Exception, e

    return None


def isnum_prefix(data):
    ret = get_prefix(data, "@")
    try:
        int(ret)
    except:
        return False
    return True


def check_id(data):
    # 1.test format
    # 2-1 is 'instance-0000001' format
    if len(data) > 9 and data[:9] == "instance-":
        instance_uuid = tool.get_uuid_by_novaid(data_id)
    elif isnum_prefix(data):
        # 2-2 is 'id' format
        id = get_prefix(data, "@")
        instance_uuid = tool.get_uuid_by_id(int(id))
    else:
        instance_uuid = data
#    # 2-3 is '10.0.0.1' format
#    instance_uuid = tool.get_uuid_by_ip(data_id)

    return instance_uuid


def plugin_heartbeat(app, db, data):
    if data is None or len(data) < 3:
        logger.debug("[ERR]invalid heartbeat data")
        return
    worker_id, update_time, status = data
#    if living_status.has_key(worker_id):
#        living_status[worker_id].update()
#    else:
#        living_status[worker_id] = LivingStatus(worker_id)
    living_state = living_status.setdefault(worker_id, LivingStatus(worker_id))
    living_state.update()
    logger.debug("heartbeat:%s" % data)
    if 0 == status:
        logger.debug("%s quited" % (worker_id))
        del living_status[worker_id]


def plugin_decoder_agent(app, db, data):
    """ data:'{"instance-00000001@pyw.novalocal":
        [
         ["cpu", "total", [1332831360.029795, 53522870000000]],
         ["mem", "total", [1332831360.029795, 131072, 131072]],
         ["nic", "vnet0", [1332831360.037399, 21795245, 5775663]],
         ["blk", "vda", [1332831360.04699, 474624, 4851712]],
         ["blk", "vdb", [1332831360.049333, 122880, 0]]
        ]
     }'
    """
    if data is None or len(data) <= 0:
        logger.debug('invalid data:%s' % (data))
        return

    print "-" * 30, "vminfo", "-" * 30
    pass_time = time.time()
    plugin_agent_srv.plugin_decoder_agent(tool, db, data)
    print 'spend \033[1;33m%f\033[0m seconds' % (time.time() - pass_time)
#    print '-' * 60


def plugin_decoder_traffic_accounting(app, db, data):
    # protocol:{'instance-00000001': ('10.0.0.2', 1332409327, '0')}
    # verify the data
    if data is None or len(data) <= 0:
        logger.debug('invalid data:%s' % (data))
        return

    print "-" * 30, "traffic", "-" * 30
    logger.debug('save traffic data:%s' % (data))
    pass_time = time.time()
#    for i in data:
#        # instance_uuid = tool.get_uuid_by_novaid(nova_id)
#        if len(i) > 0 and len(data[i]) > 2:
#            db.insert('vmnetwork', i, {data[i][0]: {data[i][1]: data[i][2]}})
    for data_id, i in data.iteritems():
        instance_uuid = check_id(data_id)
#        instance_uuid = tool.get_uuid_by_novaid(data_id)
#        if instance_uuid is None:
#            instance_uuid = data_id
#            print "Invalid instance_id format:", data_id
        if len(i) > 2:
            traffic = i[2]
            print data_id, "-->", instance_uuid, "\033[1;32m", traffic, i[1], "\033[0m"
            db.insert('vmnetwork', instance_uuid, {"total": {i[1]: traffic}})
    print 'spend \033[1;33m%f\033[0m seconds' % (time.time() - pass_time)


def SignalHandler(sig, id):
    global running

    if sig == signal.SIGUSR1:
        list_workers()
    elif sig == signal.SIGUSR2:
        clean_die_warning()
    elif sig == signal.SIGINT:
        running = False


def register_signal():
    signal.signal(signal.SIGUSR1, SignalHandler)
    signal.signal(signal.SIGUSR2, SignalHandler)
    signal.signal(signal.SIGINT, SignalHandler)
