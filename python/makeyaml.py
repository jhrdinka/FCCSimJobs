import yaml
import os
import utils as ut
from datetime import datetime

def makeyaml(outdir, uid):

    if not ut.dir_exist(outdir):
        os.system("mkdir %s"%outdir)
    
    if  outdir[-1]!='/':
        outdir+='/'
    outfile='%soutput_%s.yaml'%(outdir,uid)
    print '==========================================  ',outfile

    if ut.file_exist(outfile): return False
    data = {
        'processing' : {
            'status' : 'sending',
            'timestamp':ut.gettimestamp(),

            } 
        }

    with open(outfile, 'w') as outyaml:
        yaml.dump(data, outyaml, default_flow_style=False) 
        
    return True
