from rhapi import DEFAULT_URL, RhApi
api = RhApi(DEFAULT_URL, debug = False)

print api.folders()
#for f in api.folders():
    #print api.tables(f)

#q = "select r.runnumber from runreg_global.runs r where r.run_class_name = :class"
#p = {"class": "Collisions15" }
#qid = api.qid(q)
#print api.query(qid)

print api.count(qid, p)
print api.csv(q, p)
print api.xml(q, p)
print api.json(q, p)
