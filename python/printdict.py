#python printdict.py /afs/cern.ch/user/h/helsens/www/FCCsim_v01.txt
import json
import sys
import os.path
import re
import users as us

if len(sys.argv)!=2:
    print 'usage: python printdict.py outfile.txt'
    exit(3)


import os
def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def comma_me(amount):
    orig = amount
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', amount)
    if orig == new:
        return new
    else:
        return comma_me(new)

OutFile   = open(sys.argv[1], 'w')
ntot_events=0
ntot_files=0
ntot_fileseos=0
ntot_files_bad=0
indict=None
indictname='/afs/cern.ch/work/h/helsens/public/FCCDicts/SimulationDict_v01.json'
size_tot=0
with open(indictname) as f:
    indict = json.load(f)

mapuserstot=[]
for s, value in sorted(indict.items()):
    evttot=0
    njobs=0
    nbad=0
    print '------------------------------- ',s
    outdir="/eos/experiment/fcc/hh/simulation/samples/"+s
    nfileseos=len(os.listdir(outdir))
    mapusers=[]
    for j in value:
        if j['status']=='DONE':
            evttot+=int(j['nevents'])
            njobs+=1
        elif j['status']=='BAD':
            nbad+=1
        else:
            print 'UNKNOWN STATUS ',j['status']

        for key, value in us.users.iteritems():
            if key in j['out']:
                mapusers.append(key)
                mapuserstot.append(key)

    toaddus=''
    for key, value in us.users.iteritems():
        njobuser=sum(1 for ii in mapusers if ii == key)
        print 'user %s has njobs %i meaning %i'%(key,njobuser,int(100*njobuser/nfileseos))
        toaddus+=',,%i'%(100*njobuser/nfileseos)
    
    size=get_size(outdir)/1000000000.

    size_tot+=size
    print 'toaddus  ',toaddus
    cmd='%s,,%s,,%i,,%i,,%i,,%.2f%s\n'%(outdir,comma_me(str(evttot)),njobs,nfileseos,nbad,size,toaddus)
    OutFile.write(cmd)               
    ntot_events+=int(evttot)
    ntot_files+=int(njobs)
    ntot_files_bad+=int(nbad)
    ntot_fileseos+=int(nfileseos)
toaddustot=''
for key, value in us.users.iteritems():
    njobuser=sum(1 for ii in mapuserstot if ii == key)
    toaddustot+=',,%i'%(njobuser)

cmd='%s,,%s,,%s,,%s,,%i,,%.2f%s\n'%('total',comma_me(str(ntot_events)),comma_me(str(ntot_fileseos)),comma_me(str(ntot_files)),ntot_files_bad,size_tot,toaddustot)
OutFile.write(cmd)
