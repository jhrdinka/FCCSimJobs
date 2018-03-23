#python check_outputs.py /eos/experiment/fcc/hh/simulation/samples/v01
import glob
import os
import sys
import subprocess
import ROOT as r
import yaml
import warnings
import utils as ut
eostest='/eos/experiment/fcc/hh/tests/testfile.lhe.gz'
eostest_size=1312594
treename='events'

class checker_yaml():

#__________________________________________________________
    def __init__(self, indir, fext, process, yamldir, version):

        self.count = 0
        self.version = version
        self.yamldir = yamldir+self.version+'/'
        self.indir   = indir+self.version+'/'
        self.fext = fext
        self.yamlcheck = yamldir+self.version+'/check.yaml'
        self.process = process

#__________________________________________________________
    def dir_exist(self, mydir):
        if os.path.exists(mydir): return True
        else: return False


#__________________________________________________________
    def makeyamldir(self, outdir):
        if not self.dir_exist(outdir):
            os.system("mkdir -p %s"%outdir)
        if  outdir[-1]!='/':
            outdir+='/'
        return outdir


#__________________________________________________________
    def checkFile_root(self, f, tname):
        tf=None
        try:
            tf=r.TFile.Open(f)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except ValueError:
            print "Could read the file"
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print 'file ===%s=== must be deleted'%f
        #os.system('rm %s'%f)
            return -1,False

        tf=r.TFile.Open(f)
        tt=None
        try :
            tt=tf.Get(tname)
            if tt==None:
                try :
                    tt=tf.Get('ana/hgc')
                    if tt==None:
                        print 'file ===%s=== must be deleted'%f
                        return -1,False
                    else: tname='ana/hgc'

                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    print 'file ===%s=== must be deleted'%f
                    return -1,False

        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            
        except ValueError:
            print "Could read the file"
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print 'file ===%s=== must be deleted'%f
            return -1,False
    

        if not ut.isValidROOTfile(f):
            return -1,False
    
        f=r.TFile.Open(f)
        tt=tf.Get(tname)
        nentries=tt.GetEntries()
        if nentries==0:
            print 'file has 0 entries ===%s=== must be deleted'%f
            return 0,False
        
        print  '%i events in the file, job is good'%nentries
        return int(nentries),True


#__________________________________________________________
    def check(self, force, statfile):

        ldir=[x[0] for x in os.walk(self.indir)]
        
        if not ut.testeos(eostest,eostest_size):
            print 'eos seems to have problems, should check, will exit'
            sys.exit(3)
    
        for process in ldir:
            uid=process.replace(self.indir,"")
            if uid=="": continue
            if self.process!='' and uid!=self.process: continue
            All_files = glob.glob("%s/output_*.root"%(process))
            if len(All_files)==0:continue

            print '--------------------- ',uid
            print 'number of files  ',len(All_files)
            print 'process from the input directory ',uid

            outdir = self.makeyamldir(self.yamldir+uid)
            hasbeenchecked=False
            nevents_tot=0
            njobsdone_tot=0
            njobsbad_tot=0
            for f in All_files:

                self.count = 0
                if not os.path.isfile(f): 
                    print 'file does not exists... %s'%f
                    continue
            
                jobid=f.split('_')[-1]
                jobid=jobid.replace(self.fext,'')
                userid=ut.find_owner(f)

                outfile='%soutput_%s.yaml'%(outdir,jobid)
                if ut.file_exist(outfile) and ut.getsize(outfile)> 100 and not force: continue
                hasbeenchecked=True
                print '-----------checking root file ',f

                if '.root' in self.fext:
                    nevts, check=self.checkFile_root(f, treename)
                    status='DONE'
                    if not check: status='BAD' 

                    if status=='DONE':
                        nevents_tot+=nevts
                        njobsdone_tot+=1
                    else:
                        njobsbad_tot+=1

                    dic = {'processing':{
                            'process':uid, 
                            'jobid':jobid,
                            'nevents':nevts,
                            'status':status,
                            'out':f,
                            'size':os.path.getsize(f),
                            'user':userid
                            }
                           }
                    print '-----------writing yaml file ',outfile
                    with open(outfile, 'w') as outyaml:
                        yaml.dump(dic, outyaml, default_flow_style=False) 
                    continue
                
                else:
                    print 'not correct file extension %s'%self.fext
            
            if hasbeenchecked:
                ut.yamlstatus(self.yamlcheck, uid, False)
                cmdp='<pre>date=%s <span class="espace"/> time=%s <span class="espace"/> njobs=%i <span class="espace"/> nevents=%i <span class="espace"/> njobbad=%i <span class="espace"/> process=%s </pre>\n'%(ut.getdate_str(),ut.gettime_str() ,njobsdone_tot,nevents_tot,njobsbad_tot,uid)
                stat_exist=ut.file_exist(statfile)
                with open(statfile, "a") as myfile:
                    if not stat_exist: 
                        myfile.write('<link href="/afs/cern.ch/user/h/helsens/www/style/txtstyle.css" rel="stylesheet" type="text/css" />\n')
                        myfile.write('<style type="text/css"> /*<![CDATA[*/ .espace{ margin-left:3em } .espace2{ margin-top:9em } /*]]>*/ </style>\n')

                    myfile.write(cmdp)

                print 'date=%s  time=%s  njobs=%i  nevents=%i  njobbad=%i  process=%s'%(ut.getdate_str(),ut.gettime_str() ,njobsdone_tot,nevents_tot,njobsbad_tot,uid)




