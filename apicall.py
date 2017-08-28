from rhapi import RhApi

API_URL = 'http://gem-machine-a:8113'
q = 'select c.part_serial_number,c.IMON_UA, c.GAIN, c.GAIN_ERROR from gem_omds.c4260 c'

api = RhApi(API_URL, debug = False)
data = api.json(q)
print data
