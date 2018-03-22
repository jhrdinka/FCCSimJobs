#For RECO
#python send_reco.py -q 1nh -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/20GeV/NTUP/ -i  /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/20GeV/SIMU/

#python send_reco.py -q 1nh -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/100GeV/NTUP/ -i  /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/100GeV/SIMU/

#python send_reco.py -q 8nh -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/200GeV/NTUP/ -i  /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/200GeV/SIMU/

#python send_reco.py -q 8nh -o /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/500GeV/NTUP/ -i  /eos/experiment/fcc/hh/simulation/samples/tracker_calobarrel/diJets/500GeV/SIMU/

import glob, os, sys,subprocess,cPickle
import commands
import time
import random
from datetime import datetime
import ROOT as r

#__________________________________________________________
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}

#__________________________________________________________
def SubmitToBatch(cmd,nbtrials):
    submissionStatus=0
    for i in range(nbtrials):            
        outputCMD = getCommandOutput(cmd)
        stderr=outputCMD["stderr"].split('\n')

        for line in stderr :
            if line=="":
                print "------------GOOD SUB"
                submissionStatus=1
                break
            else:
                print "++++++++++++ERROR submitting, will retry"
                print "error: ",stderr
                print "Trial : "+str(i)+" / "+str(nbtrials)
                time.sleep(10)
                break
            
        if submissionStatus==1:
            jobid=outputCMD["stdout"].split()[1].replace("<","").replace(">","")
            return 1,jobid
        
        if i==nbtrials-1:
            print "failed sumbmitting after: "+str(nbtrials)+" trials, will exit"
            return 0,0

#__________________________________________________________
if __name__=="__main__":
    Dir = os.getcwd()
    
    user=os.environ['USER']

    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option ('-i', '--inputeos',  help='eos input',
                       dest='inputeos',
                       default='')

    parser.add_option ('-q', '--queue',  help='lxbatch queue, default 8nh',
                       dest='queue',
                       default='8nh')

    parser.add_option ('-o', '--outputeos',  help='eos output',
                       dest='outputeos',
                       default='')


    (options, args) = parser.parse_args()
    inputeos   = options.inputeos
    queue      = options.queue
    outputeos  = options.outputeos
    rundir = os.getcwd()
    nbjobsSub=0

    import glob
    All_files = glob.glob("%s/output_*.root"%(inputeos))
    print "will submit %i jobs"%(len(All_files))
    
    for i in xrange(len(All_files)):
        seed = int(datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
        uniqueID='%s_%i'%(user,seed)

#        infile=All_files[i].split('/')[-1]
#        print infile
#        infile2=infile.replace('-','').replace('.','').replace(':','').replace('root','.root')
#        print infile2
#        sys.exit(1)
        logdir=Dir+"/BatchOutputs/"
        os.system("mkdir -p %s"%logdir)
        frunname = 'job_%s.sh'%(uniqueID)
        infile=All_files[i].split('/')[-1]

        frun = None
        try:
            frun = open(logdir+'/'+frunname, 'w')
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            time.sleep(10)
            frun = open(logdir+'/'+frunname, 'w')

        import os.path
        if os.path.isfile(All_files[i].replace('SIMU','NTUP')):
            tf1=r.TFile.Open(All_files[i].replace('SIMU','NTUP'))
            tt1=tf1.Get('ana/hgc')
            n1=tt1.GetEntries()

            if os.path.isfile(All_files[i]):
                tf2=r.TFile.Open(All_files[i])
                tt2=tf2.Get('events')

                n2=tt2.GetEntries()
                if n1==n2: 
                    print "file %s with %i entries already exists, continue"%(All_files[i],n1)
                    continue

        commands.getstatusoutput('chmod 777 %s/%s'%(logdir,frunname))
        frun.write('#!/bin/bash\n')
        frun.write('unset LD_LIBRARY_PATH\n')
        frun.write('unset PYTHONHOME\n')
        frun.write('unset PYTHONPATH\n')
        frun.write('export JOBDIR=$PWD\n')
        frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/\n')
        frun.write('source ./init.sh\n')
        frun.write('cd /afs/cern.ch/user/h/helsens/FCCsoft/Calo/FCCSW/FCCSimJobs/\n')
        frun.write('export EOS_MGM_URL=\"root://eospublic.cern.ch\"\n')
        frun.write('python eoscopy.py %s $JOBDIR/%s\n'%(All_files[i],infile))
        frun.write('python Convert.py $JOBDIR/%s $JOBDIR/%s\n'%(infile,infile.replace('.root','.root_out')))
        frun.write('python eoscopy.py $JOBDIR/%s %s\n'%(infile.replace('.root','.root_out'),All_files[i].replace('SIMU','NTUP')))

        cmdBatch="bsub -M 2000000 -R \"rusage[pool=2000]\" -q %s -cwd%s %s" %(queue, logdir,logdir+'/'+frunname)
        batchid=-1
        job,batchid=SubmitToBatch(cmdBatch,10)
        nbjobsSub+=job

    print 'succesfully sent %i  jobs'%nbjobsSub
