import sys
import os.path
import re
import yaml
import utils as ut
import users as us

class printer():

#__________________________________________________________
    def __init__(self, indir,eosdir, outfile, version):
        self.basedir = indir
        self.indir    = indir+version
        self.outfile  = outfile
        self.eosdir = eosdir
        self.OutFile   = open(self.outfile, 'w')
        self.yamlcheck = indir+version+'/check.yaml'

        self.tot_size=0
        self.ntot_events=0
        self.ntot_files=0
        self.ntot_bad=0
        self.ntot_eos=0
        self.ntot_sumw=0


#__________________________________________________________
    def comma_me(self, amount):
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)


#__________________________________________________________
    def run(self):
        usermaptot={}
        for key, value in us.users.iteritems():
            usermaptot[key]=0
        ldir=[x[0] for x in os.walk(self.indir)]
        for l in ldir:
            mergefile=l+'/merge.yaml'
            if not ut.file_exist(mergefile): continue
            process = l.replace(self.basedir,'')
            print '--------------  process  ',process

            tmpf=None
            with open(mergefile, 'r') as stream:
                try:
                    tmpf = yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

            events_tot=tmpf['merge']['nevents']
            size_tot=tmpf['merge']['size']/1000000000.
            bad_tot=tmpf['merge']['nbad']
            files_tot=tmpf['merge']['ndone']
            sumw_tot=0
            nfileseos=0
            if files_tot+bad_tot!=0:
                nfileseos=len(os.listdir('%s%s'%(self.eosdir,process)))
    
            print 'nevents               : %i'%events_tot
            print 'nfiles on eos/checked good/checked bad : %i/%i/%i'%(nfileseos,files_tot,bad_tot)
            marked_b=''
            marked_e=''

            if nfileseos>files_tot+bad_tot:
                ut.yamlstatus(self.yamlcheck, process, False)
                marked_b='<h2><mark>'
                marked_e='</mark></h2>'

            self.ntot_events+=int(events_tot)
            self.ntot_files+=int(files_tot)
            self.tot_size+=float(size_tot)
            self.ntot_bad+=int(bad_tot)
            self.ntot_eos+=int(nfileseos)

            usermap={}
            for key, value in us.users.iteritems():
                usermap[key]=0
            for key, value in iter(sorted(tmpf['merge']['users'].iteritems())):
                usermap[key]=value
                usermaptot[key]=usermaptot[key]+value

            toaddus=''
            for key, value in iter(sorted(usermap.iteritems())):
                toaddus+=',,%i'%(value)

            cmd='%s,,%s,,%s%i%s,,%s%i%s,,%i,,%.2f%s\n'%(process,
                                                        self.comma_me(str(events_tot)),
                                                        marked_b,files_tot,marked_e,
                                                        marked_b,nfileseos,marked_e,
                                                        bad_tot,size_tot,toaddus)
            self.OutFile.write(cmd)               

   


        toaddustot=''
        for key, value in iter(sorted(usermaptot.iteritems())):
            toaddustot+=',,%i'%(value)
   
        cmd='%s,,%s,,%s,,%s,,%s,,%.2f%s\n'%('total',self.comma_me(str(self.ntot_events)),self.comma_me(str(self.ntot_files)),
                                            self.comma_me(str(self.ntot_eos)),self.comma_me(str(self.ntot_bad)),
                                            self.tot_size,toaddustot)
        self.OutFile.write(cmd)
