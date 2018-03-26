yamldir='/afs/cern.ch/work/h/helsens/public/FCCDicts/yaml/FCC/simu/'
indir='/eos/experiment/fcc/hh/simulation/samples/'
statfile='/afs/cern.ch/user/h/helsens/www/data/statsimu_FCC.html'
webfile='/afs/cern.ch/user/h/helsens/www/data/FCCsim_VERSION.txt'


#__________________________________________________________
if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser()

    jobTypeGroup = parser.add_mutually_exclusive_group(required = True) # Type of events to generate
    jobTypeGroup.add_argument("--check", action='store_true', help="run the jobchecker")
    jobTypeGroup.add_argument("--merge", action='store_true', help="merge the yaml for all the processes")
    jobTypeGroup.add_argument("--clean", action='store_true', help="clean the dictionnary and eos from bad jobs")
    jobTypeGroup.add_argument("--cleanold", action='store_true', help="clean the yaml from old jobs (more than 72 hours)")
    jobTypeGroup.add_argument("--web", action='store_true', help="print the dictionnary for webpage")
    jobTypeGroup.add_argument("--remove", action='store_true', help="remove a specific process from the dictionary and from eos" )

    parser.add_argument('-p','--process', type=str, help='Name of the process to use to send jobs or for the check', default='')
    parser.add_argument('--force', action='store_true', help='Force the type of process', default=False)
    parser.add_argument('--version', type=str, help='Version to use', choices = ['v01', 'v02_pre', 'v02', 'v03'])
    args, _ = parser.parse_known_args()

    if args.check:
        print 'running the check'
        if args.process!='':
            print 'using a specific process ',args.process
        import checker_yaml as chky
        print args.process
        checker=chky.checker_yaml(indir, '.root', args.process,  yamldir, args.version)
        checker.check(args.force, statfile)

    elif args.merge:
        print 'running the merger'
        if args.process!='':
            print 'using a specific process ',args.process
        import merger as mgr
        merger = mgr.merger(args.process, yamldir, args.version)
        merger.merge(args.force)


    elif args.clean:
        print 'clean the dictionnary and eos'
        import cleaner as clf
        clean=clf.cleaner(indir, yamldir, args.process, args.version)
        clean.clean()


    elif args.cleanold:
        print 'clean the dictionnary from old jobs that have not been checked'
        import cleaner as clf
        clean=clf.cleaner(indir, yamldir, args.process, args.version)
        clean.cleanoldjobs()

    elif args.web:
        import printer as prt
        webfile=webfile.replace('VERSION', args.version)
        printdic=prt.printer(yamldir,indir,webfile, args.version)
        printdic.run()

