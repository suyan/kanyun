# encoding: utf-8
# TAB char: space
#
# Author: Peng Yuwei<yuwei5@staff.sina.com.cn>
# Last update: Peng Yuwei<yuwei5@staff.sina.com.cn> 2012-3-19

import json
import sys
import traceback
import pycassa

"""
db struce:
+-------------------------------------+
| cf=cpu/mem/...(one item one cf )    |
+-------------------------------------+---------+
| scf=total/devname                             |
+==============+==============+=======+=========+
|              | col=utc_time | time2 | ...     |
+==============+==============+=======+=========+
| key=instance | val1(subval) | val2  | ...     |
+===============================================+

db data format:
cf = pycassa.ColumnFamily(db, 'cpu')
cf.insert('instance', {u'total': {1332389700: 11}})
cf.insert('instance', {u'blk': {1332389700: (22, 33)}})

data format:
{"instance@hostname": 
    [
        ('cpu', 'total', (utc_time, cpu_time)), 
        ('mem', 'total', (utc_time, max, free)), 
        ('nic', 'vnet8', (utc_time, incoming, outgoing(内网))), 
        ('blk', 'vda', (utc_time, read, write)), 
        ('blk', 'vdb', (utc_time, read, write))
    ]
}
example:
{"instance-00000001@pyw.novalocal": 
    [
        ["cpu", "total", [1332465360.033008, 9043400000000]], 
        ["mem", "total", [1332465360.033008, 131072, 131072]], 
        ["nic", "vnet0", [1332465360.038922, 3860180, 1025563]], 
        ["blk", "vda", [1332465360.044262, 474624, 4741120]], 
        ["blk", "vdb", [1332465360.046606, 122880, 0]]
    ]
}
"""

# ColumnFamilys object collection
cfs = dict()

# previous data
# data format: {key: (value, D-value, instance_id, cf_str, scf_str)}
# example: {'/instance_0001#host/cpu/total/1': (92345, 12, 'instance_0001#host', 'cpu', 'total')}
previous_data = dict()

def get_change(prekey, data):
    # prekey: /instance_0001#host/cpu/total/
    # data: ["cpu", "total", [1332465360.033008, 9043400000000]],
    val1 = 0
    val2 = None
    new_value = data[2]
    if previous_data.has_key(prekey + "/1"):
        o = previous_data[prekey + "/1"]
        val1 = new_value[1] - o[0]
        print '\t1:%s --> %s (%d)' % (new_value[1], o[0], val1)
    else:
        val1 = new_value[1]
        print '\t1:%s' % (val1)
                
    if data[0] != 'cpu': 
        if previous_data.has_key(prekey + "/2"):
            o = previous_data[prekey + "/2"]
            val2 = new_value[2] - o[0]
            print '\t2:%s --> %s (%d)' % (new_value[2], o[0], val2)
        else:
            val2 = new_value[2]
            print '\t2:%s' % (val2)
            
    return val1, val2

def plugin_decoder_agent(db, data):
    if len(data) <= 0:
        print 'invalid data:', data
        return
        
    if db is None:
        return
        
    pre_data = None
    for instance_id, data in data.iteritems():
        keypath = '/' # for previous_data's key
        keypath += instance_id
        print '*****instance=%s:%d ColumnFamilys*****' % (instance_id, len(cfs))

        for i in data:
            # i is ["cpu", "total", [1332465360.033008, 9043400000000]], 
            cf_str = i[0]
            scf_str = i[1]
            if not cfs.has_key(cf_str):
                cfs[cf_str] = pycassa.ColumnFamily(db, cf_str)
                print 'create cf connection:', cf_str
            
            cf = cfs[cf_str]
            
#           // get change
            prekey = keypath + '/' + cf_str + '/' + scf_str
            val1, val2 = get_change(prekey, i)
            
            value = i[2]
            if val2 is None:
                previous_data[prekey + '/1'] = (value[1], val1, instance_id, cf_str, scf_str)
                cf.insert(instance_id, {cf_str: {int(value[0]): str(val1)}})
                print '\t%s saved' % (prekey)
                print '\tkey=%s, cf=%s saved' % (instance_id, cf_str)
            else:
                previous_data[prekey + '/1'] = (value[1], val1, instance_id, cf_str, scf_str)
                previous_data[prekey + '/2'] = (value[2], val2, instance_id, cf_str, scf_str)
                cf.insert(instance_id, {cf_str + '1': {int(value[0]): str(val1)}})
                cf.insert(instance_id, {cf_str + '2': {int(value[0]): str(val2)}})
                print '\t%s saved\n\t%s saved' % (prekey + '/1', prekey + '/2')
                print '\tkey=%s, cf=%s 2 records saved' % (instance_id, cf_str)

    print '\t%d buffer' % (len(previous_data))
    print '-' * 60
    
    
if __name__ == '__main__':
    test_str = """
    {"instance-00000001@pyw.novalocal": 
    [
        ["cpu", "total", [1332465360.033008, 9043400000000]], 
        ["mem", "total", [1332465360.033008, 131072, 131072]], 
        ["nic", "vnet0", [1332465360.038922, 3860180, 1025563]], 
        ["blk", "vda", [1332465360.044262, 474624, 4741120]], 
        ["blk", "vdb", [1332465360.046606, 122880, 0]]
    ]
}
    """
    test_data = json.loads(test_str)
    plugin_decoder_agent(None, test_data)