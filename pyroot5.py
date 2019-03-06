
from rhapi import DEFAULT_URL, RhApi
api = RhApi(DEFAULT_URL, debug = False)

API_URL = 'http://gem-machine-a:8113'
q = 'select c.part_serial_number,c.IMON_UA, c.GAIN, c.GAIN_ERROR from gem_omds.c4260 c'

api = RhApi(API_URL, debug = False)
data = api.json(q)
print (data)

"""
print api.folders()
print ('a ')
for f in api.folders():
    print (api.tables(f))
print ('b ')

q = "select r.runnumber from runreg_global.runs r where r.run_class_name = :class"
p = {"class": "Collisions15" }
qid = api.qid(q)
print (api.query(qid))
print ('c ')

print (api.count(qid, p))
print (api.csv(q, p))
#print (api.xml(q, p))
print (api.json(q, p))
"""
