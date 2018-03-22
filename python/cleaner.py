import yaml
import os
import glob
import os.path
import sys
import utils as ut

class cleaner():

#__________________________________________________________
    def __init__(self, indir, yamldir, process, version):
        self.indir = indir+'/'+version+'/'+process
        self.yamldir = yamldir+'/'+version+'/'+process
        self.yamlcheck = yamldir+self.version+'/check.yaml'
        self.process = process

#__________________________________________________________
    def clean(self):
        nfailed=0
        All_files = []
        if self.process=='':
            All_files = glob.glob("%s/merge.yaml"%self.yamldir)
        else:
            ldir=[x[0] for x in os.walk(self.indir)]
            for l in ldir:
                files = glob.glob("%s/merge.yaml"%l)
                if len(files)>0: All_files.extend(files)

        print All_files
        sys.exit(3)
        for f in All_files:
            print '=====================    ',f
            with open(f, 'r') as stream:
                try:
                    tmpf = yaml.load(stream)
                    if tmpf['merge']['nbad']==0:continue
                    nfailed+=tmpf['merge']['nbad']
                    for r in tmpf['merge']['outfilesbad']:
                        cmd="rm %s/%s"%(tmpf['merge']['outdir'],r)
                        print 'remove  file  %s   from process  %s'%(r, tmpf['merge']['process'])
                        os.system(cmd)

                        if self.process=='':
                            cmd="rm %s/%s/%s"%(self.yamldir,tmpf['merge']['process'],r.replace('.lhe.gz','.yaml').replace('.root','.yaml'))
                            os.system(cmd)

                        else:
                            cmd="rm %s/%s"%(self.yamldir,r.replace('.lhe.gz','.yaml').replace('.root','.yaml'))
                            os.system(cmd)

                        ut.yamlstatus(self.yamlcheck,tmpf['merge']['process'] , False)
                    
                except yaml.YAMLError as exc:
                    print(exc)

        print 'removed %i files'%nfailed

#__________________________________________________________
    def cleanoldjobs(self):
        ldir=[]
        if self.process=='':
            ldir=next(os.walk(self.yamldir))[1]
        else: ldir=[self.process]

        #ldir=[x[0] for x in os.walk(self.yamldir)]
        print ldir
       
        for l in ldir:
            All_files = []
            if self.process=='':
                All_files = glob.glob("%s/%s/events_*.yaml"%(self.yamldir,l))
            else:
                All_files = glob.glob("%s/events_*.yaml"%(self.yamldir))

            if len(All_files)==0:continue
            process=l            
            if self.process!='' and self.process!=process: 
                continue

            print 'process from the input directory ',process

            for f in All_files:
                if not os.path.isfile(f): 
                    print 'file does not exists... %s'%f
                    continue
                
                with open(f, 'r') as stream:
                    try:
                       tmpf = yaml.load(stream)
                       if tmpf['processing']['status']=='sending':
                           if ut.gettimestamp() - tmpf['processing']['timestamp']>8000:
                               print 'job %s is running since too long, will delete the yaml'%(f)

                           cmd="rm %s"%(f)
                           print cmd
                           os.system(cmd)

                    except yaml.YAMLError as exc:
                        print(exc)
                    except IOError as e:
                        print(e)
                        

   
