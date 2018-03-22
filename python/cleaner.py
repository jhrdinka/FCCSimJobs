import json
import os
dicname='/afs/cern.ch/work/h/helsens/public/FCCDicts/SimulationDict_v01.json'
mydict=None
with open(dicname) as f:
    mydict = json.load(f)
user=os.environ['USER']

for s in mydict:
    for j in mydict[s]:
        if j['status']=='DONE':
            continue
        elif j['status']=='BAD' and user in j['out']: 
            if not os.path.exists(j['out']):
                print 'BAD job already removed from eos   %s'%j['out']
            else:
                print  'remove BAD job from eos   %s'%j['out']
                os.system('rm %s'%j['out'])

            
